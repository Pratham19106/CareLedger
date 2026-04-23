import os
import json
import sys
import tempfile
from dotenv import load_dotenv

# Always resolve env from backend/.env, independent of process cwd.
PROJECT_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTENV_PATH = os.path.join(PROJECT_BACKEND_DIR, ".env")
load_dotenv(dotenv_path=DOTENV_PATH)
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['FLAGS_call_stack_level'] = '2'

from ocr_init import OCRManager
import fitz  # PyMuPDF — used for PDF → image conversion
from google import genai
from google.genai import types
from ollama import Client

# ── API SELECTION ──────────────────────────────────────────────────────────────
USE_GEMINI = False
USE_OLLAMA = True
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "deepseek-v3.2:cloud")

# ── Initialize Clients ─────────────────────────────────────────────────────────
if USE_GEMINI:
    gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

if not USE_GEMINI:
    ollama_api_key = (os.environ.get('OLLAMA_API_KEY') or '').strip()
    ollama_headers = {'Authorization': f'Bearer {ollama_api_key}'} if ollama_api_key else None
    ollama_client = Client(
        host="http://localhost:11434",
        headers=ollama_headers
    )

# ── Global OCR Manager (Persistent) ────────────────────────────────────────────
ocr_manager = None

PLACEHOLDER_DRUG = {
    "drug_name": "UNKNOWN",
    "dosage": "UNKNOWN",
    "frequency": "UNKNOWN",
    "duration_days": -1,
}

SYSTEM_PROMPT = """You are a strict medical prescription parser. Your ONLY job is to extract medication information from OCR text and return valid JSON.

RULES — read carefully:
1. Extract ONLY: drug_name, dosage, frequency, duration_days.
2. Ignore everything else — doctor names, patient info, clinic addresses, dates, diagnoses, stamps, etc.
3. If the OCR text contains NO recognizable drug/medication information, return:
   {"error": "NO_PRESCRIPTION_DATA", "drugs": []}
4. If a specific field cannot be determined for a drug, use "UNKNOWN" for strings and -1 for duration_days.
5. NEVER invent or hallucinate drug names, dosages, or frequencies not present in the text.
6. duration_days must be an integer (e.g. 7, 14, 30) or -1 if not found.
7. frequency must be a human-readable string: e.g. "Once daily", "Twice daily", "Every 8 hours", "As needed".
8. Return ONLY raw JSON — no markdown, no explanation, no preamble.
9. The Drug Name Usually ends with Tablet or Syrup
OUTPUT FORMAT (strictly follow this):
{ "date" :"DD/MM/YYYY",
  "drugs": [
    {
      "drug_name": "string",
      "dosage": "string",
      "frequency": "string",
      "duration_days": integer
    }
  ]
}
"""


def emit_message(msg_type: str, data: dict):
    """Emit a message to Node.js (JSON line)"""
    message = {"type": msg_type}
    message.update(data)
    print(json.dumps(message))
    sys.stdout.flush()


def emit_checkpoint(step: str, status: str, message: str = "", data: dict = None, request_id: str = None):
    """Emit a checkpoint for progress tracking"""
    payload = {
        "checkpoint": step,
        "status": status,
        "message": message,
        "data": data or {}
    }
    if request_id:
        payload["request_id"] = request_id
    emit_message("checkpoint", payload)


def parse_prescription(ocr_text: str, request_id: str = "unknown") -> dict:
    """Parse OCR text using LLM (Gemini or Ollama)"""
    if not ocr_text.strip():
        emit_checkpoint(
            "PARSING",
            "warning",
            "Skipping LLM parsing because OCR text is empty",
            {"ocr_text_length": 0},
            request_id=request_id,
        )
        return {"error": "EMPTY_OCR_TEXT", "drugs": []}

    emit_checkpoint(
        "PARSING",
        "in_progress",
        "Starting LLM structuring",
        {
            "engine": "gemini" if USE_GEMINI else "ollama",
            "model": "gemini-2.0-flash" if USE_GEMINI else OLLAMA_MODEL,
            "ocr_text_length": len(ocr_text),
        },
        request_id=request_id,
    )

    raw = ""

    try:
        # ── Using Gemini API ───────────────────────────────────────────────────
        if USE_GEMINI:
            emit_checkpoint(
                "LLM_CALL",
                "in_progress",
                "Calling Gemini structurer",
                {"model": "gemini-2.0-flash"},
                request_id=request_id,
            )
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=1024,
                    temperature=0,
                ),
                contents=f"Parse this prescription OCR text:\n\n{ocr_text}",
            )
            raw = response.text.strip()
            emit_checkpoint(
                "LLM_CALL",
                "completed",
                "Gemini structurer returned response",
                {"response_length": len(raw)},
                request_id=request_id,
            )

        # ── Using Ollama API ───────────────────────────────────────────────────
        else:
            emit_checkpoint(
                "LLM_CALL",
                "in_progress",
                "Calling Ollama structurer",
                {"model": OLLAMA_MODEL, "host": "http://localhost:11434"},
                request_id=request_id,
            )
            messages = [
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT,
                },
                {
                    'role': 'user',
                    'content': f"Parse this prescription OCR text:\n\n{ocr_text}",
                },
            ]
            response_text = ""
            for part in ollama_client.chat(OLLAMA_MODEL, messages=messages, stream=True, think=False):
                response_text += part['message']['content']
            raw = response_text.strip()
            emit_checkpoint(
                "LLM_CALL",
                "completed",
                "Ollama structurer returned response",
                {"response_length": len(raw)},
                request_id=request_id,
            )

        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        parsed = json.loads(raw)

        if "drugs" not in parsed:
            raise ValueError("Missing 'drugs' key in response")

        validated_drugs = []
        for drug in parsed["drugs"]:
            validated_drugs.append(
                {
                    "drug_name": str(drug.get("drug_name", "UNKNOWN")),
                    "dosage": str(drug.get("dosage", "UNKNOWN")),
                    "frequency": str(drug.get("frequency", "UNKNOWN")),
                    "duration_days": int(drug.get("duration_days", -1)),
                }
            )

        emit_checkpoint(
            "PARSING",
            "completed",
            f"LLM structuring parsed {len(validated_drugs)} drug rows",
            {"drugs_count": len(validated_drugs)},
            request_id=request_id,
        )

        return {"drugs": validated_drugs}

    except json.JSONDecodeError as e:
        emit_checkpoint(
            "PARSING",
            "warning",
            f"JSON decode failed: {str(e)}",
            request_id=request_id,
        )
        return {"error": "PARSE_FAILED", "drugs": [PLACEHOLDER_DRUG]}

    except Exception as e:
        emit_checkpoint(
            "PARSING",
            "warning",
            f"LLM parsing error: {str(e)}",
            {"error_type": type(e).__name__},
            request_id=request_id,
        )
        return {"error": "LLM_ERROR", "drugs": [PLACEHOLDER_DRUG]}


def convert_pdf_to_images(pdf_path: str) -> list:
    """
    Convert ALL pages of a PDF to temporary PNG images.

    Uses PyMuPDF (fitz) to render each page at 2× zoom (~144 DPI),
    which gives PaddleOCR enough resolution to read prescription text.

    Returns:
        list[str]: Absolute paths to the temporary PNG files (one per page),
                   ordered by page number.
                   Caller is responsible for deleting all returned files.
    """
    doc = fitz.open(pdf_path)
    zoom_matrix = fitz.Matrix(2, 2)  # 2× zoom → ~144 DPI
    temp_paths = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pixmap = page.get_pixmap(matrix=zoom_matrix, alpha=False)

        # Named temp file that persists until explicitly deleted
        tmp = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
            prefix=f"ocr_pdf_p{page_num}_"
        )
        tmp.close()  # Close handle so PyMuPDF can write to it on Windows
        pixmap.save(tmp.name)
        temp_paths.append(tmp.name)

    doc.close()
    return temp_paths


def cleanup_temp_files(paths: list):
    """Delete a list of temp file paths, silently ignoring any errors."""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.unlink(p)
        except Exception:
            pass


def process_request(image_path: str, request_id: str):
    """Process a single OCR request"""
    try:
        emit_checkpoint(
            "REQUEST",
            "in_progress",
            "OCR request received",
            {"image_path": image_path},
            request_id=request_id,
        )

        # ── Checkpoint 1: File Validation ──────────────────────────────────
        emit_checkpoint("FILE_CHECK", "in_progress", f"Checking if file exists: {image_path}", request_id=request_id)

        if not os.path.exists(image_path):
            emit_checkpoint("FILE_CHECK", "failed", f"File not found: {image_path}", request_id=request_id)
            emit_message("done", {"request_id": request_id, "success": False})
            return

        emit_checkpoint("FILE_CHECK", "completed", "File verified", request_id=request_id)

        # ── Checkpoint 1b: PDF → Images Conversion (all pages) ────────────
        pdf_temp_paths = []  # Track temp files so we can delete them later
        ocr_image_paths = [image_path]  # Default: single image file
        file_ext = os.path.splitext(image_path)[1].lower()

        if file_ext == ".pdf":
            emit_checkpoint("PDF_CONVERT", "in_progress", "Detected PDF — converting all pages to images", request_id=request_id)
            try:
                pdf_temp_paths = convert_pdf_to_images(image_path)
                ocr_image_paths = pdf_temp_paths  # Run OCR on each page
                emit_checkpoint(
                    "PDF_CONVERT", "completed",
                    f"PDF converted: {len(pdf_temp_paths)} page(s) ready for OCR",
                    request_id=request_id,
                )
            except Exception as e:
                emit_checkpoint("PDF_CONVERT", "failed", f"PDF conversion failed: {str(e)}", request_id=request_id)
                emit_message("done", {"request_id": request_id, "success": False, "error": str(e)})
                return

        # ── Checkpoint 2: Ensure OCR is initialized ────────────────────────
        emit_checkpoint("OCR_CHECK", "in_progress", "Checking OCR initialization status", request_id=request_id)

        if ocr_manager.is_initialized():
            emit_checkpoint("OCR_CHECK", "completed", "OCR already initialized", request_id=request_id)
        else:
            emit_checkpoint("OCR_INIT", "failed", "OCR manager not initialized", request_id=request_id)
            emit_message("done", {"request_id": request_id, "success": False})
            return

        # ── Checkpoint 3: Run OCR Prediction (all pages) ───────────────────
        total_pages = len(ocr_image_paths)
        emit_checkpoint(
            "OCR_PREDICTION", "in_progress",
            f"Running OCR on {total_pages} page(s)",
            request_id=request_id,
        )

        try:
            ocr = ocr_manager.get_ocr()
            ocr_text = ""

            for page_idx, page_image_path in enumerate(ocr_image_paths):
                result = ocr.predict(page_image_path)
                page_text = ""
                for res in result:
                    page_text += "\n".join(res["rec_texts"]) + "\n"

                if total_pages > 1:
                    ocr_text += f"--- Page {page_idx + 1} ---\n{page_text}\n"
                else:
                    ocr_text += page_text

            emit_checkpoint("OCR_PREDICTION", "completed", "OCR prediction completed", {
                "pages_processed": total_pages,
                "text_length": len(ocr_text),
                "lines_detected": len(ocr_text.strip().split("\n"))
            }, request_id=request_id)

        except Exception as e:
            emit_checkpoint("OCR_PREDICTION", "failed", f"OCR prediction failed: {str(e)}", request_id=request_id)
            cleanup_temp_files(pdf_temp_paths)
            emit_message("done", {"request_id": request_id, "success": False})
            return

        # ── Checkpoint 4: Parse Prescription ───────────────────────────────
        emit_checkpoint("PARSING", "in_progress", "Parsing prescription data with LLM", request_id=request_id)

        prescription = parse_prescription(ocr_text.strip(), request_id=request_id)

        if prescription.get("error"):
            emit_checkpoint("PARSING", "warning", f"Parsing completed with warning: {prescription.get('error')}", request_id=request_id)
        else:
            emit_checkpoint("PARSING", "completed", f"Parsed {len(prescription.get('drugs', []))} drugs", request_id=request_id)

        # ── Checkpoint 5: Complete ────────────────────────────────────────
        completion_status = "success"
        completion_message = "Prescription processing completed"
        if prescription.get("error"):
            completion_status = "warning"
            completion_message = f"Prescription processing completed with parser warning: {prescription.get('error')}"

        emit_checkpoint("COMPLETE", completion_status, completion_message, prescription, request_id=request_id)

        # ── Signal completion ──────────────────────────────────────────────
        cleanup_temp_files(pdf_temp_paths)  # Remove all PDF page temp files

        emit_message("done", {
            "request_id": request_id,
            "success": True,
            "prescription": prescription
        })

    except Exception as e:
        emit_checkpoint("COMPLETE", "failed", f"Unexpected error: {str(e)}", request_id=request_id)
        # Clean up all PDF page temp files on unexpected errors too
        if 'pdf_temp_paths' in locals():
            cleanup_temp_files(pdf_temp_paths)
        emit_message("done", {"request_id": request_id, "success": False, "error": str(e)})


def initialize_ocr():
    """Initialize OCR manager (runs once at startup)"""
    global ocr_manager
    
    emit_message("status", {
        "message": "Initializing OCR manager",
        "status": "initializing"
    })
    
    ocr_manager = OCRManager()
    result = ocr_manager.initialize()
    
    if result.get("initialized"):
        emit_message("status", {
            "message": "OCR manager initialized successfully",
            "status": "ready",
            "initialized": True
        })
        return True
    else:
        emit_message("status", {
            "message": f"OCR initialization failed: {result.get('error')}",
            "status": "failed",
            "initialized": False
        })
        return False


def main():
    """Main worker loop"""
    print("[WORKER] OCR Persistent Worker Starting...", file=sys.stderr)
    
    # Initialize OCR on startup
    if not initialize_ocr():
        print("[WORKER] Failed to initialize OCR. Exiting.", file=sys.stderr)
        sys.exit(1)
    
    print("[WORKER] Ready to receive requests", file=sys.stderr)
    
    # Listen for requests from Node.js on stdin
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                image_path = request.get("image_path")
                request_id = request.get("request_id", "unknown")
                
                if not image_path:
                    emit_message("error", {
                        "request_id": request_id,
                        "message": "Missing image_path in request"
                    })
                    continue
                
                print(f"[WORKER] Processing request {request_id}: {image_path}", file=sys.stderr)
                process_request(image_path, request_id)
                
            except json.JSONDecodeError as e:
                print(f"[WORKER] Invalid JSON received: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"[WORKER] Error processing request: {e}", file=sys.stderr)
                continue
                
    except KeyboardInterrupt:
        print("[WORKER] Shutting down gracefully...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"[WORKER] Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

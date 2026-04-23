import base64
import json
import os
import sys
import tempfile
from typing import List

import fitz  # PyMuPDF
from dotenv import load_dotenv
from ollama import Client

# Always resolve env from backend/.env, independent of process cwd.
PROJECT_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTENV_PATH = os.path.join(PROJECT_BACKEND_DIR, ".env")
load_dotenv(dotenv_path=DOTENV_PATH)

OLLAMA_HOST = (os.environ.get("OLLAMA_HOST") or "https://ollama.com").strip()
OLLAMA_MODEL = (os.environ.get("OLLAMA_VLM_MODEL") or os.environ.get("OLLAMA_MODEL") or "gemma4").strip()
OLLAMA_API_KEY = (os.environ.get("OLLAMA_API_KEY") or "").strip()
OLLAMA_TEMPERATURE = float((os.environ.get("OLLAMA_VLM_TEMPERATURE") or "0.15").strip())
OLLAMA_SEED = int((os.environ.get("OLLAMA_VLM_SEED") or "42").strip())
ollama_client = None

PLACEHOLDER_DRUG = {
    "drug_name": "UNKNOWN",
    "dosage": "UNKNOWN",
    "frequency": "UNKNOWN",
    "duration_days": -1,
}

SYSTEM_PROMPT = """You are a strict medical prescription parser. Your ONLY job is to extract medication information from prescription images and return valid JSON.

RULES - read carefully:
1. Extract ONLY: drug_name, dosage, frequency, duration_days.
2. Ignore everything else - doctor names, patient info, clinic addresses, dates, diagnoses, stamps, etc.
3. If the image contains NO recognizable drug/medication information, return:
   {\"error\": \"NO_PRESCRIPTION_DATA\", \"drugs\": []}
4. If a specific field cannot be determined for a drug, use \"UNKNOWN\" for strings and -1 for duration_days.
5. NEVER invent or hallucinate drug names, dosages, or frequencies not present in the text.
6. duration_days must be an integer (e.g. 7, 14, 30) or -1 if not found.
7. frequency must be a human-readable English string: e.g. \"Once daily in morning\", \"Twice daily in morning and night\", \"Every 8 hours\", \"As needed\".
    Reference: 1-0-1 means \"Twice daily in morning and night\".
    If frequency is written in Marathi (example: \"जेवणाआधी - दररोज\"), translate to English and store in frequency.
8. Return ONLY raw JSON - no markdown, no explanation, no preamble.
9. The Drug Name Usually ends with Tablet or Syrup
10. Determinism rules:
     - Keep output order consistent with visual top-to-bottom reading order.
     - Use exact text from prescription when available; do not paraphrase unless translating Marathi frequency to English
     use human readable text for 1-0-1 to twice daily in morning and night, 1-0-0 for once in morning.

     - For repeated runs on the same input, produce the same JSON structure and field formatting.
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

USER_PROMPT = """Parse the attached prescription image(s) and return strict JSON only.
Apply deterministic extraction and keep drug order stable by visual reading order.
If no prescription medication details are visible, return:
{\"error\": \"NO_PRESCRIPTION_DATA\", \"drugs\": []}
"""


def emit_message(msg_type: str, data: dict):
    message = {"type": msg_type}
    message.update(data)
    print(json.dumps(message))
    sys.stdout.flush()


def emit_checkpoint(step: str, status: str, message: str = "", data: dict = None, request_id: str = None):
    payload = {
        "checkpoint": step,
        "status": status,
        "message": message,
        "data": data or {},
    }
    if request_id:
        payload["request_id"] = request_id
    emit_message("checkpoint", payload)


def convert_pdf_to_images(pdf_path: str) -> List[str]:
    doc = fitz.open(pdf_path)
    zoom_matrix = fitz.Matrix(2, 2)
    temp_paths: List[str] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pixmap = page.get_pixmap(matrix=zoom_matrix, alpha=False)

        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix=f"vlm_pdf_p{page_num}_")
        tmp.close()
        pixmap.save(tmp.name)
        temp_paths.append(tmp.name)

    doc.close()
    return temp_paths


def cleanup_temp_files(paths: List[str]):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.unlink(p)
        except Exception:
            pass


def read_image_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def strip_markdown_fences(raw: str) -> str:
    if not raw:
        return raw

    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
    return text


def normalize_and_validate(parsed: dict) -> dict:
    if "drugs" not in parsed:
        raise ValueError("Missing 'drugs' key in response")

    validated_drugs = []
    for drug in parsed.get("drugs", []):
        validated_drugs.append(
            {
                "drug_name": str(drug.get("drug_name", "UNKNOWN")),
                "dosage": str(drug.get("dosage", "UNKNOWN")),
                "frequency": str(drug.get("frequency", "UNKNOWN")),
                "duration_days": int(drug.get("duration_days", -1)),
            }
        )

    result = {"drugs": validated_drugs}
    if "error" in parsed:
        result["error"] = parsed.get("error")
    return result


def parse_prescription_from_images(image_paths: List[str], request_id: str = "unknown") -> dict:
    emit_checkpoint(
        "PARSING",
        "in_progress",
        "Starting VLM parsing from images",
        {
            "engine": "ollama",
            "model": OLLAMA_MODEL,
            "host": OLLAMA_HOST,
            "image_count": len(image_paths),
        },
        request_id=request_id,
    )

    try:
        emit_checkpoint(
            "LLM_CALL",
            "in_progress",
            "Calling vision language model",
            {"model": OLLAMA_MODEL, "host": OLLAMA_HOST},
            request_id=request_id,
        )

        encoded_images = [read_image_as_base64(image_path) for image_path in image_paths]

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT,
                "images": encoded_images,
            },
        ]

        stream = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            stream=True,
            options={
                "temperature": OLLAMA_TEMPERATURE,
                "seed": OLLAMA_SEED,
            },
        )
        response_text = ""
        for part in stream:
            response_text += part["message"]["content"]

        raw = strip_markdown_fences(response_text)

        emit_checkpoint(
            "LLM_CALL",
            "completed",
            "Vision language model returned response",
            {"response_length": len(raw)},
            request_id=request_id,
        )

        parsed = json.loads(raw)
        normalized = normalize_and_validate(parsed)

        emit_checkpoint(
            "PARSING",
            "completed",
            f"VLM parsing extracted {len(normalized.get('drugs', []))} drug rows",
            {"drugs_count": len(normalized.get("drugs", []))},
            request_id=request_id,
        )

        return normalized

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
            f"VLM parsing error: {str(e)}",
            {"error_type": type(e).__name__},
            request_id=request_id,
        )
        return {"error": "LLM_ERROR", "drugs": [PLACEHOLDER_DRUG]}


def process_request(image_path: str, request_id: str):
    pdf_temp_paths: List[str] = []
    try:
        emit_checkpoint(
            "REQUEST",
            "in_progress",
            "OCR request received",
            {"image_path": image_path},
            request_id=request_id,
        )

        emit_checkpoint("FILE_CHECK", "in_progress", f"Checking if file exists: {image_path}", request_id=request_id)

        if not os.path.exists(image_path):
            emit_checkpoint("FILE_CHECK", "failed", f"File not found: {image_path}", request_id=request_id)
            emit_message("done", {"request_id": request_id, "success": False})
            return

        emit_checkpoint("FILE_CHECK", "completed", "File verified", request_id=request_id)

        ocr_image_paths = [image_path]
        file_ext = os.path.splitext(image_path)[1].lower()

        if file_ext == ".pdf":
            emit_checkpoint("PDF_CONVERT", "in_progress", "Detected PDF - converting all pages to images", request_id=request_id)
            try:
                pdf_temp_paths = convert_pdf_to_images(image_path)
                ocr_image_paths = pdf_temp_paths
                emit_checkpoint(
                    "PDF_CONVERT",
                    "completed",
                    f"PDF converted: {len(pdf_temp_paths)} page(s) ready for VLM",
                    request_id=request_id,
                )
            except Exception as e:
                emit_checkpoint("PDF_CONVERT", "failed", f"PDF conversion failed: {str(e)}", request_id=request_id)
                emit_message("done", {"request_id": request_id, "success": False, "error": str(e)})
                return

        prescription = parse_prescription_from_images(ocr_image_paths, request_id=request_id)

        if prescription.get("error"):
            emit_checkpoint(
                "COMPLETE",
                "warning",
                f"Prescription processing completed with parser warning: {prescription.get('error')}",
                prescription,
                request_id=request_id,
            )
        else:
            emit_checkpoint(
                "COMPLETE",
                "completed",
                "Prescription processing completed",
                prescription,
                request_id=request_id,
            )

        emit_message(
            "done",
            {
                "request_id": request_id,
                "success": True,
                "prescription": prescription,
            },
        )

    except Exception as e:
        emit_checkpoint("COMPLETE", "failed", f"Unexpected error: {str(e)}", request_id=request_id)
        emit_message("done", {"request_id": request_id, "success": False, "error": str(e)})
    finally:
        cleanup_temp_files(pdf_temp_paths)


def initialize_worker() -> bool:
    emit_message(
        "status",
        {
            "message": "Initializing VLM OCR worker",
            "status": "initializing",
            "pipeline": "vlm",
            "model": OLLAMA_MODEL,
            "host": OLLAMA_HOST,
        },
    )

    host_lower = OLLAMA_HOST.lower()
    is_local_host = host_lower.startswith("http://localhost") or host_lower.startswith("http://127.0.0.1")

    if not OLLAMA_API_KEY and not is_local_host:
        emit_message(
            "status",
            {
                "message": "OLLAMA_API_KEY is missing. Set it in backend/.env for cloud usage.",
                "status": "failed",
                "initialized": False,
            },
        )
        return False

    try:
        emit_checkpoint("WORKER_INIT", "in_progress", "Creating Ollama client")

        headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else None
        global ollama_client
        ollama_client = Client(host=OLLAMA_HOST, headers=headers)

        emit_message(
            "status",
            {
                "message": "VLM OCR worker initialized successfully",
                "status": "ready",
                "initialized": True,
                "pipeline": "vlm",
                "model": OLLAMA_MODEL,
                "host": OLLAMA_HOST,
            },
        )
        return True
    except Exception as e:
        emit_message(
            "status",
            {
                "message": f"VLM OCR worker initialization failed: {str(e)}",
                "status": "failed",
                "initialized": False,
            },
        )
        return False


def main():
    print("[WORKER] VLM OCR Persistent Worker Starting...", file=sys.stderr)

    if not initialize_worker():
        print("[WORKER] Failed to initialize VLM worker. Exiting.", file=sys.stderr)
        sys.exit(1)

    print("[WORKER] Ready to receive requests", file=sys.stderr)

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
                    emit_message(
                        "error",
                        {
                            "request_id": request_id,
                            "message": "Missing image_path in request",
                        },
                    )
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

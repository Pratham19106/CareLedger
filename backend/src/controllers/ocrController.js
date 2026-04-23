const fs = require('fs');
const pdfParse = require('pdf-parse');
const pool = require('../config/db');
const { successResponse, errorResponse } = require('../utils/responseFormatter');
const ocrManager = require('../utils/ocrManager');
const PrescriptionService = require('../services/prescriptionService');

async function removeTempFile(filePath) {
    if (!filePath) return;
    try {
        await fs.promises.unlink(filePath);
    } catch (err) {
        // Ignore missing file errors during cleanup.
        if (err?.code !== 'ENOENT') {
            console.error('Error deleting temporary file:', err);
        }
    }
}

async function assertSinglePagePdf(filePath, mimetype) {
    if (mimetype !== 'application/pdf') {
        return;
    }

    let parsed;
    try {
        const fileBuffer = await fs.promises.readFile(filePath);
        parsed = await pdfParse(fileBuffer);
    } catch (err) {
        const parseError = new Error('Unable to read PDF file. Please upload a valid single-page PDF.');
        parseError.code = 'VALIDATION_ERROR';
        throw parseError;
    }

    if (Number(parsed?.numpages || 0) !== 1) {
        const singlePageError = new Error('Only single-page PDF documents are supported for legacy upload.');
        singlePageError.code = 'VALIDATION_ERROR';
        throw singlePageError;
    }
}

function normalizeField(value) {
    return String(value || '').trim().toUpperCase();
}

function isDefaultDrugRow(drug) {
    const name = normalizeField(drug?.drug_name);
    const dosage = normalizeField(drug?.dosage);
    const frequency = normalizeField(drug?.frequency);
    const duration = Number(drug?.duration_days);

    return (
        name === 'UNKNOWN'
        && dosage === 'UNKNOWN'
        && frequency === 'UNKNOWN'
        && (!Number.isFinite(duration) || duration === -1)
    );
}

function isDefaultOcrResponse(prescriptionData) {
    if (!prescriptionData || typeof prescriptionData !== 'object') {
        return true;
    }

    if (prescriptionData.error) {
        return true;
    }

    const drugs = Array.isArray(prescriptionData.drugs) ? prescriptionData.drugs : [];
    if (drugs.length === 0) {
        return true;
    }

    return drugs.every((drug) => isDefaultDrugRow(drug));
}

async function runOcrAndSavePrescription({ filePath, mimetype, consultationId, patientId, doctorId, doctorNotes, enforceSinglePagePdf = false }) {
    const checkpoints = [];

    if (enforceSinglePagePdf) {
        await assertSinglePagePdf(filePath, mimetype);
    }

    const status = ocrManager.getStatus();
    if (!status.isReady) {
        const notReady = new Error('OCR service is initializing. Please retry in a few moments.');
        notReady.code = 'OCR_NOT_READY';
        notReady.status = 503;
        notReady.meta = { status };
        throw notReady;
    }

    const result = await ocrManager.processRequest(
        filePath,
        (checkpoint) => {
            checkpoints.push(checkpoint);
        }
    );

    const prescriptionData = result?.prescription || { drugs: [] };

    if (isDefaultOcrResponse(prescriptionData)) {
        const readError = new Error('Error reading the document. Please upload a clearer prescription document.');
        readError.code = 'DOCUMENT_READ_FAILED';
        throw readError;
    }

    const prescriptionId = await PrescriptionService.savePrescription(
        prescriptionData,
        consultationId,
        patientId,
        doctorId,
        doctorNotes || null
    );

    return {
        checkpoints,
        prescriptionId,
        drugsCount: Array.isArray(prescriptionData?.drugs) ? prescriptionData.drugs.length : 0,
    };
}

/**
 * Main OCR scan endpoint
 * Handles file upload and delegates to persistent OCR worker
 */
const ocrScan = async (req, res, next) => {
    if (!req.file) {
        return errorResponse(res, 400, 'VALIDATION_ERROR', 'No file uploaded');
    }

    // Extract IDs from request body
    const { consultation_id, patient_id, doctor_id, doctor_notes } = req.body || {};

    const filePath = req.file.path;

    try {
        const outcome = await runOcrAndSavePrescription({
            filePath,
            mimetype: req.file.mimetype,
            consultationId: consultation_id || null,
            patientId: patient_id || null,
            doctorId: doctor_id || null,
            doctorNotes: doctor_notes || null,
            enforceSinglePagePdf: false,
        });

        return successResponse(
            res,
            200,
            {
                prescription_id: outcome.prescriptionId,
                drugs_count: outcome.drugsCount,
                success: true,
            },
            'Prescription saved successfully'
        );
    } catch (err) {
        console.error('[OCR_SCAN_ERROR]', err.message);

        if (err.code === 'DOCUMENT_READ_FAILED') {
            return errorResponse(res, 400, 'DOCUMENT_READ_FAILED', err.message);
        }

        if (err.code === 'VALIDATION_ERROR') {
            return errorResponse(res, 400, 'VALIDATION_ERROR', err.message);
        }

        if (err.code === 'OCR_NOT_READY') {
            return errorResponse(
                res,
                err.status || 503,
                'OCR_NOT_READY',
                err.message,
                err.meta || {}
            );
        }

        return errorResponse(
            res,
            500,
            'OCR_PROCESSING_ERROR',
            err.message
        );
    } finally {
        await removeTempFile(filePath);
    }
};

const ocrScanLegacyForPatient = async (req, res, next) => {
    if (!req.file) {
        return errorResponse(res, 400, 'VALIDATION_ERROR', 'No file uploaded');
    }

    const filePath = req.file.path;

    try {
        const userId = req.user?.id;
        const role = req.user?.role;

        if (!userId || role !== 'patient') {
            return errorResponse(res, 403, 'FORBIDDEN', 'Only patients can upload legacy documents');
        }

        const patientProfile = await pool.query(
            `SELECT id FROM patients WHERE user_id = $1`,
            [userId]
        );

        if (patientProfile.rowCount === 0) {
            return errorResponse(res, 404, 'NOT_FOUND', 'Patient profile not found');
        }

        const patientId = patientProfile.rows[0].id;

        const outcome = await runOcrAndSavePrescription({
            filePath,
            mimetype: req.file.mimetype,
            consultationId: null,
            patientId,
            doctorId: null,
            doctorNotes: 'Imported from legacy prescription document using OCR.',
            enforceSinglePagePdf: true,
        });

        return successResponse(
            res,
            200,
            {
                prescription_id: outcome.prescriptionId,
                drugs_count: outcome.drugsCount,
                source: 'legacy_upload',
                success: true,
            },
            'Legacy prescription imported successfully'
        );
    } catch (err) {
        console.error('[OCR_LEGACY_SCAN_ERROR]', err.message);

        if (err.code === 'DOCUMENT_READ_FAILED') {
            return errorResponse(res, 400, 'DOCUMENT_READ_FAILED', err.message);
        }

        if (err.code === 'VALIDATION_ERROR') {
            return errorResponse(res, 400, 'VALIDATION_ERROR', err.message);
        }

        if (err.code === 'OCR_NOT_READY') {
            return errorResponse(
                res,
                err.status || 503,
                'OCR_NOT_READY',
                err.message,
                err.meta || {}
            );
        }

        return errorResponse(
            res,
            500,
            'OCR_PROCESSING_ERROR',
            err.message
        );
    } finally {
        await removeTempFile(filePath);
    }
};

const ocrHealth = (req, res, next) => {
    const status = ocrManager.getStatus();

    if (status.isReady) {
        return successResponse(
            res,
            200,
            {
                status: 'healthy',
                ready: true,
                pendingRequests: status.pendingRequests
            },
            'OCR service is healthy'
        );
    } else {
        return successResponse(
            res,
            202,
            {
                status: 'initializing',
                ready: false,
                initializing: status.isInitializing
            },
            'OCR service is initializing'
        );
    }
};

module.exports = { ocrScan, ocrScanLegacyForPatient, ocrHealth };

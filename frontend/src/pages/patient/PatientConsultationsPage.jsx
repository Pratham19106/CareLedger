import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { jsPDF } from 'jspdf';
import { getOwnPatientProfile, getPatientPrescriptionById, getPatientPrescriptions } from '../../api/patients';
import { formatConsultationId, formatDate, titleCase, toDateInputValue } from '../../utils/formatters';

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function matchesPrescriptionSearch(row, rawQuery) {
  const query = String(rawQuery || '').trim().toLowerCase();
  if (!query) return true;

  const doctorName = String(row?.doctor_name || '').toLowerCase();
  const dateValue = row?.reference_date || row?.issued_at;
  const formattedDate = String(formatDate(dateValue) || '').toLowerCase();
  const isoDate = String(toDateInputValue(dateValue) || '').toLowerCase();

  let monthShort = '';
  let monthLong = '';
  let day = '';
  let year = '';
  const parsed = new Date(dateValue);
  if (!Number.isNaN(parsed.getTime())) {
    monthShort = parsed.toLocaleString('en-US', { month: 'short' }).toLowerCase();
    monthLong = parsed.toLocaleString('en-US', { month: 'long' }).toLowerCase();
    day = String(parsed.getDate());
    year = String(parsed.getFullYear());
  }

  const dateSearchBlob = [formattedDate, isoDate, monthShort, monthLong, day, year]
    .filter(Boolean)
    .join(' ');

  return doctorName.includes(query) || dateSearchBlob.includes(query);
}

function buildPatientPrescriptionPreviewHtml(prescription, selectedPrescription, patientProfile) {
  if (!prescription) return '';

  const patientName = patientProfile?.full_name || 'Patient';
  const patientHealthId = patientProfile?.health_id || 'N/A';
  const consultationDisplayId = formatConsultationId(prescription.consultation_id || selectedPrescription?.consultation_id);
  const when = formatDate(prescription.issued_at || selectedPrescription?.reference_date || selectedPrescription?.issued_at);
  const clinicName = prescription.clinic_name || selectedPrescription?.clinic_name || 'Clinic';
  const clinicAddress = prescription.clinic_address || selectedPrescription?.clinic_address || 'Address not available';
  const clinicPhone = prescription.clinic_phone || selectedPrescription?.clinic_phone || 'Not available';
  const clinicEmail = prescription.clinic_email || selectedPrescription?.clinic_email || 'Not available';
  const doctorName = prescription.doctor_name || selectedPrescription?.doctor_name || 'Attending Doctor';

  const logoHtml = `<div class="rx-logo-fallback">${escapeHtml(clinicName.slice(0, 2).toUpperCase())}</div>`;

  const itemRows = (prescription.items || [])
    .map(
      (item, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${escapeHtml(item.drug_name)}</td>
          <td>${escapeHtml(item.dosage)}</td>
          <td>${escapeHtml(item.frequency)}</td>
          <td>${escapeHtml(item.prescribed_for || '-')}</td>
          <td>${escapeHtml(item.duration_days)}</td>
        </tr>
      `,
    )
    .join('');

  const continuedRows = (prescription.continued_medications || [])
    .map(
      (medication, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${escapeHtml(medication.name || '-')}</td>
          <td>${escapeHtml(medication.dosage || '-')}</td>
          <td>${escapeHtml(medication.prescibed_for || '-')}</td>
          <td>${escapeHtml(formatDate(medication.prescibed_at) || '-')}</td>
        </tr>
      `,
    )
    .join('');

  const continuedMedicationsHtml = (prescription.continued_medications || []).length > 0
    ? `
      <h3 class="rx-subtitle">Continued Medications</h3>
      <table class="rx-table rx-table-continued">
        <thead>
          <tr>
            <th>#</th>
            <th>Medicine</th>
            <th>Dosage</th>
            <th>Prescribed For</th>
            <th>Since</th>
          </tr>
        </thead>
        <tbody>${continuedRows}</tbody>
      </table>
    `
    : `
      <h3 class="rx-subtitle">Continued Medications</h3>
      <p class="rx-subtext">No continued medications.</p>
    `;

  const notesHtml = prescription.doctor_notes
    ? `<p class="rx-notes"><strong>Doctor's Notes:</strong> ${escapeHtml(prescription.doctor_notes)}</p>`
    : `<p class="rx-notes"><strong>Notes:</strong> Follow dosage schedule exactly as prescribed. In case of adverse reaction, seek medical care immediately.</p>`;

  return `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>E-Prescription</title>
        <style>
          @page { size: A4; margin: 18mm; }
          body { font-family: Arial, sans-serif; color: #15232a; margin: 0; }
          .rx-paper { border: 1px solid #d4dde4; border-radius: 10px; overflow: hidden; }
          .rx-header { display: grid; grid-template-columns: 80px 1fr; gap: 14px; align-items: center; padding: 16px; background: linear-gradient(180deg, #f4f9f8, #ffffff); border-bottom: 1px solid #d9e4e8; }
          .rx-logo-fallback { width: 64px; height: 64px; border-radius: 10px; display: grid; place-items: center; font-weight: 700; color: #1a4a4a; background: #e7f1ef; border: 1px solid #c9ddda; }
          .rx-clinic h1 { margin: 0; font-size: 20px; }
          .rx-clinic p { margin: 3px 0 0; font-size: 12px; color: #35505f; }
          .rx-body { padding: 14px 16px 10px; }
          .rx-title { margin: 0 0 10px; font-size: 18px; letter-spacing: 0.02em; }
          .rx-meta { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 16px; margin-bottom: 14px; font-size: 12px; }
          .rx-meta p { margin: 0; }
          .rx-subtitle { margin: 16px 0 8px; font-size: 14px; color: #223741; }
          .rx-subtext { margin: 0; font-size: 12px; color: #546974; }
          .rx-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
          .rx-table th, .rx-table td { border: 1px solid #d2dde4; padding: 8px; text-align: left; font-size: 12px; }
          .rx-table th { background: #edf4f7; }
          .rx-table-continued { margin-top: 6px; }
          .rx-notes { margin-top: 14px; font-size: 12px; color: #2f4652; }
          .rx-footer { margin-top: 18px; border-top: 1px dashed #b8c8d2; padding: 12px 16px 16px; display: grid; grid-template-columns: 1fr 220px; gap: 12px; align-items: end; }
          .rx-footer p { margin: 0; font-size: 12px; color: #395260; }
          .rx-sign { text-align: center; }
          .rx-sign-line { margin-top: 22px; border-top: 1px solid #738896; padding-top: 4px; font-size: 11px; color: #3f5562; }
        </style>
      </head>
      <body>
        <article class="rx-paper">
          <header class="rx-header">
            ${logoHtml}
            <div class="rx-clinic">
              <h1>${escapeHtml(clinicName)}</h1>
              <p>${escapeHtml(clinicAddress)}</p>
              <p>Doctor: ${escapeHtml(doctorName)}</p>
              <p>Phone: ${escapeHtml(clinicPhone)} | Email: ${escapeHtml(clinicEmail)}</p>
            </div>
          </header>

          <section class="rx-body">
            <h2 class="rx-title">E-Prescription</h2>
            <div class="rx-meta">
              <p><strong>Patient:</strong> ${escapeHtml(patientName)}</p>
              <p><strong>Health ID:</strong> ${escapeHtml(patientHealthId)}</p>
              <p><strong>Consultation ID:</strong> ${escapeHtml(consultationDisplayId)}</p>
              <p><strong>Date:</strong> ${escapeHtml(when)}</p>
              <p><strong>Doctor:</strong> ${escapeHtml(doctorName)}</p>
            </div>

            <table class="rx-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Medicine</th>
                  <th>Dosage</th>
                  <th>Frequency</th>
                  <th>Prescribed For</th>
                  <th>Duration (days)</th>
                </tr>
              </thead>
              <tbody>${itemRows}</tbody>
            </table>

            ${continuedMedicationsHtml}

            ${notesHtml}
          </section>

          <footer class="rx-footer">
            <p>Generated digitally by CareLedger Clinical Workspace.</p>
            <div class="rx-sign">
              <div class="rx-sign-line">${escapeHtml(doctorName)}</div>
            </div>
          </footer>
        </article>
      </body>
    </html>
  `;
}

function PatientConsultationsPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedPrescription, setSelectedPrescription] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: patientProfileRes } = useQuery({
    queryKey: ['patient-profile'],
    queryFn: getOwnPatientProfile,
  });
  const patientProfile = patientProfileRes?.data || null;

  const { data: prescriptionsRes, isLoading: loading, error: fetchError } = useQuery({
    queryKey: ['patient-prescriptions'],
    queryFn: getPatientPrescriptions,
  });
  const prescriptions = prescriptionsRes?.data || [];
  const filteredPrescriptions = useMemo(
    () => prescriptions.filter((row) => matchesPrescriptionSearch(row, searchQuery)),
    [prescriptions, searchQuery]
  );
  const error = fetchError ? fetchError?.response?.data?.error?.message || 'Failed to load past prescriptions.' : '';

  const { data: prescriptionRes, isLoading: prescriptionLoading, error: presError } = useQuery({
    queryKey: ['patient-prescription', selectedPrescription?.prescription_id],
    queryFn: () => getPatientPrescriptionById(selectedPrescription.prescription_id),
    enabled: !!selectedPrescription?.prescription_id,
    retry: false,
  });
  const prescription = prescriptionRes?.data || null;
  const prescriptionError = presError ? presError?.response?.data?.error?.message || 'Prescription could not be loaded.' : '';

  const prescriptionPreviewHtml = useMemo(
    () => buildPatientPrescriptionPreviewHtml(prescription, selectedPrescription, patientProfile),
    [prescription, selectedPrescription, patientProfile]
  );

  const openPrescription = (record) => {
    setSelectedPrescription(record);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedPrescription(null);
  };

  const downloadPrescriptionPdf = async () => {
    if (!prescriptionPreviewHtml || !selectedPrescription) {
      return;
    }

    let frame = null;
    try {
      setDownloadingPdf(true);

      frame = document.createElement('iframe');
      frame.setAttribute('aria-hidden', 'true');
      frame.style.position = 'fixed';
      frame.style.left = '-99999px';
      frame.style.top = '0';
      frame.style.width = '794px';
      frame.style.height = '1123px';
      frame.style.opacity = '0';
      frame.style.pointerEvents = 'none';
      document.body.appendChild(frame);

      await new Promise((resolve) => {
        frame.onload = () => resolve();
        frame.srcdoc = prescriptionPreviewHtml;
      });

      const frameDoc = frame.contentDocument;
      if (!frameDoc?.body) {
        throw new Error('Unable to prepare PDF content.');
      }

      if (frameDoc.fonts?.ready) {
        await frameDoc.fonts.ready;
      }

      const imageLoadPromises = Array.from(frameDoc.images || []).map((image) => {
        if (image.complete) return Promise.resolve();
        return new Promise((resolve) => {
          image.onload = () => resolve();
          image.onerror = () => resolve();
        });
      });
      await Promise.all(imageLoadPromises);

      const { default: html2canvas } = await import('html2canvas');
      const previewRoot = frameDoc.querySelector('.rx-paper') || frameDoc.body;

      const canvas = await html2canvas(previewRoot, {
        scale: 2,
        useCORS: true,
        allowTaint: false,
        backgroundColor: '#ffffff',
        logging: false,
        windowWidth: Math.max(previewRoot.scrollWidth, 794),
        windowHeight: previewRoot.scrollHeight,
      });

      const doc = new jsPDF({ unit: 'pt', format: 'a4' });
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const renderWidth = pageWidth;

      const fullImageHeight = (canvas.height * renderWidth) / canvas.width;
      const pagePixelHeight = Math.floor((pageHeight * canvas.width) / renderWidth);

      if (fullImageHeight <= pageHeight) {
        const imageData = canvas.toDataURL('image/png', 1.0);
        doc.addImage(imageData, 'PNG', 0, 0, renderWidth, fullImageHeight, undefined, 'FAST');
      } else {
        const pageCanvas = document.createElement('canvas');
        pageCanvas.width = canvas.width;
        const pageContext = pageCanvas.getContext('2d');
        if (!pageContext) {
          throw new Error('Unable to create canvas context for PDF export.');
        }

        let renderedPixels = 0;
        let pageIndex = 0;

        while (renderedPixels < canvas.height) {
          const sliceHeight = Math.min(pagePixelHeight, canvas.height - renderedPixels);
          pageCanvas.height = sliceHeight;

          pageContext.clearRect(0, 0, pageCanvas.width, sliceHeight);
          pageContext.drawImage(
            canvas,
            0,
            renderedPixels,
            canvas.width,
            sliceHeight,
            0,
            0,
            pageCanvas.width,
            sliceHeight,
          );

          const pageImage = pageCanvas.toDataURL('image/png', 1.0);
          const pageRenderHeight = (sliceHeight * renderWidth) / canvas.width;

          if (pageIndex > 0) {
            doc.addPage();
          }
          doc.addImage(pageImage, 'PNG', 0, 0, renderWidth, pageRenderHeight, undefined, 'FAST');

          renderedPixels += sliceHeight;
          pageIndex += 1;
        }
      }

      const safeConsultationId = formatConsultationId(selectedPrescription.consultation_id || selectedPrescription.prescription_id);
      const safePatient = String(patientProfile?.full_name || 'patient')
        .replace(/[^a-zA-Z0-9-_]+/g, '_')
        .replace(/^_+|_+$/g, '');
      doc.save(`prescription_${safePatient || 'patient'}_${safeConsultationId}.pdf`);
    } finally {
      setDownloadingPdf(false);
      if (frame?.parentNode) {
        frame.parentNode.removeChild(frame);
      }
    }
  };

  return (
    <section className="panel luxe-section-card patient-page-luxe">
      <div className="panel-head">
        <h3>Past Prescriptions</h3>
        <span className="luxe-subtle-count">{filteredPrescriptions.length} entries</span>
      </div>

      <div className="patient-consultations-toolbar">
        <input
          type="text"
          className="patient-consultations-search"
          placeholder="Search by doctor or date (e.g., Ru, 17 Apr 2026, 2026-04-17)"
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
        />
      </div>

      {loading ? <p className="muted">Loading past prescriptions...</p> : null}
      {error ? <p className="error-text">{error}</p> : null}

      <div className="patient-consultations-table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Doctor</th>
              <th>Date</th>
              <th>Source</th>
              <th>Items</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredPrescriptions.map((row) => (
              <tr key={row.prescription_id}>
                <td>{row.doctor_name || '-'}</td>
                <td>{formatDate(row.reference_date || row.issued_at)}</td>
                <td>
                  <span className={`status-pill ${row.is_legacy_import ? 'warn' : 'success'}`}>
                    {row.is_legacy_import ? 'Legacy Import' : titleCase(row.status || 'completed')}
                  </span>
                </td>
                <td>{row.items_count || 0}</td>
                <td>
                  <button type="button" className="text-btn" onClick={() => openPrescription(row)}>
                    View Details
                  </button>
                </td>
              </tr>
            ))}
            {!loading && filteredPrescriptions.length === 0 ? (
              <tr>
                <td className="patient-empty" colSpan={5}>
                  No prescriptions match your search.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>

      {modalOpen ? (
        <div className="modal-overlay" role="dialog" aria-modal="true" onClick={closeModal}>
          <div className="modal-card modal-card-sticky-footer" onClick={(event) => event.stopPropagation()}>
            <div className="panel-head split">
              <h3>Prescription Details</h3>
              <button className="text-btn" type="button" onClick={closeModal}>
                Close
              </button>
            </div>

            {selectedPrescription ? (
              <div className="modal-info-bar">
                <p style={{ margin: '0 0 6px 0' }}><strong>Recorded:</strong> {new Date(selectedPrescription.reference_date || selectedPrescription.issued_at).toLocaleString()}</p>
                <p style={{ margin: '0 0 6px 0' }}><strong>Source:</strong> {selectedPrescription.is_legacy_import ? 'Legacy upload' : 'Consultation'}</p>
                <p style={{ margin: 0 }}><strong>Consultation ID:</strong> {formatConsultationId(selectedPrescription.consultation_id)}</p>
              </div>
            ) : null}

            {prescriptionLoading ? <p className="muted">Loading details...</p> : null}
            {!prescriptionLoading && !prescription && !prescriptionError ? <p className="muted">No prescription details available.</p> : null}
            {prescriptionError ? <p className="error-text">{prescriptionError}</p> : null}

            {!prescriptionLoading && prescriptionPreviewHtml ? (
              <div className="consult-pdf-preview consult-pdf-preview-scrollable">
                <iframe className="consultation-pdf-frame" title="Prescription Preview" srcDoc={prescriptionPreviewHtml} />
              </div>
            ) : null}

            <div className="modal-footer-sticky">
              <button
                type="button"
                className="submit-btn slim"
                onClick={downloadPrescriptionPdf}
                disabled={!prescriptionPreviewHtml || downloadingPdf}
              >
                {downloadingPdf ? 'Downloading...' : 'Download PDF'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default PatientConsultationsPage;

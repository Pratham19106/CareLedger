# CareLedger — Doctor UI Design Document

> Comprehensive frontend design specification for the **Doctor Portal**.
> Refer to [FRONTEND_DESIGN_SYSTEM.md](./FRONTEND_DESIGN_SYSTEM.md) for colors, typography, and shared components.

---

## 1. Overview

The Doctor Portal is the clinical workspace where verified doctors manage their profile, clinics, consultations, prescriptions, patient medications, and handle emergencies. The tone is **professional, efficient, and data-dense** — doctors need quick access to critical information without clutter.

**Role Accent:** Teal (`#14B8A6`)

---

## 2. Information Architecture

```
Doctor Portal
├── Dashboard (Home)
├── My Profile
│   ├── View / Edit Profile
│   └── Verification Status
├── My Clinics
│   ├── Clinic List
│   ├── Add Clinic
│   └── Edit / Delete Clinic
├── Consultations
│   ├── All Consultations
│   ├── Start New Consultation
│   ├── Consultation Detail
│   │   ├── Update Status
│   │   └── Prescription Management
│   └── View Prescription
├── Patient Lookup
│   └── View Patient Profile (via access permission)
├── Active Medications
│   ├── Search by Patient
│   ├── Add Medication
│   ├── Edit Medication
│   └── Delete Medication
├── Emergency Mode
│   └── Emergency Patient Data
├── OCR Prescription Scanner
└── Settings / Logout
```

---

## 3. Sidebar Navigation

| Icon              | Label              | Route                         |
|-------------------|--------------------|-------------------------------|
| `layout-dashboard`| Dashboard          | `/doctor/dashboard`           |
| `user`            | My Profile         | `/doctor/profile`             |
| `building-2`     | My Clinics          | `/doctor/clinics`             |
| `stethoscope`    | Consultations       | `/doctor/consultations`       |
| `pill`           | Medications         | `/doctor/medications`         |
| `alert-triangle` | Emergency           | `/doctor/emergency`           |
| `scan`           | OCR Scanner         | `/doctor/ocr`                 |
| `settings`       | Settings            | `/doctor/settings`            |
| `log-out`        | Logout              | *(action)*                    |

---

## 4. Pages

### 4.1 Dashboard

**Purpose:** Overview of the doctor's current workload and verification status.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  👋 Welcome, Dr. {full_name}                             │
│  {specialization} · License: {license_number}            │
│  Verification: [✅ Verified] or [⏳ Pending]              │
├──────────────┬──────────────┬────────────────────────────┤
│  STAT CARD   │  STAT CARD   │  STAT CARD                │
│  Active      │  Completed   │  Clinics                  │
│  Consults    │  Consults    │  Registered               │
│  count: {n}  │  count: {n}  │  count: {n}               │
├──────────────┴──────────────┴────────────────────────────┤
│                                                          │
│  🕐 Recent Consultations                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │ John Doe · HLTH-123 · Mar 15, 2026 · 🔄 Active  │    │
│  │ Jane Smith · HLTH-456 · Mar 14 · ✅ Completed    │    │
│  └──────────────────────────────────────────────────┘    │
│                        [ View All Consultations → ]      │
│                                                          │
│  ⚡ Quick Actions                                        │
│  [ Start Consultation ] [ Scan Prescription ] [ 🆘 Emergency ] │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Verification Banner:** If `is_verified = false`, show a prominent warning banner at the top:
> ⚠️ Your profile is pending admin verification. Consultation features are disabled until verification is complete.

This banner should use `--warning` background at 15% opacity, `--warning` text, and include a `shield-alert` icon.

**API Calls on Load:**
| API                               | Purpose                      |
|-----------------------------------|------------------------------|
| `GET /api/doctors/`               | Profile, verification status |
| `GET /api/doctors/consultations`  | Consultation list + counts   |
| `GET /api/clinics/`               | Clinic count                 |

---

### 4.2 My Profile

**Purpose:** View and edit doctor profile.

**Profile Card:**

```
┌──────────────────────────────────┐
│  ┌────┐                         │
│  │ 🩺 │  Dr. Smith              │
│  └────┘  Cardiology             │
│                                  │
│  🆔 License:  MED-123456        │
│  ✅ Verified:  Yes               │
│  📧 Email:    drsmith@example.com│
│  📱 Phone:    9999999999         │
│                                  │
│  [ ✏️ Edit Profile ]             │
└──────────────────────────────────┘
```

**Edit Modal:**

| Field            | Input Type | Validation | Notes                     |
|------------------|------------|------------|---------------------------|
| `full_name`      | Text       | Required   |                           |
| `specialization` | Text       | Optional   |                           |

> 🔒 `license_number` and `is_verified` are **read-only** — cannot be changed by the doctor.

**API Calls:**
| Action | API                  |
|--------|----------------------|
| Load   | `GET /api/doctors/`  |
| Save   | `PUT /api/doctors/`  |

---

### 4.3 My Clinics

**Purpose:** Full CRUD for the doctor's clinic locations.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  My Clinics                            [ + Add Clinic ]  │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐    │
│  │  🏥 Heart Care Center                            │    │
│  │  📍 123 Main St, City                            │    │
│  │  📧 clinic@example.com · 📱 5555555555           │    │
│  │  🖼️ [clinic logo thumbnail]          ✏️  🗑️     │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  🏥 Downtown Medical                             │    │
│  │  📍 456 Health Ave                               │    │
│  │  📧 downtown@example.com · 📱 6666666666         │    │
│  │                                       ✏️  🗑️     │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Add/Edit Modal:**

| Field       | Input Type | Validation | Notes              |
|-------------|------------|------------|--------------------|
| `clinicName`| Text       | Required   | Clinic name        |
| `address`   | Text       | Required   | Full address       |
| `email`     | Email      | Required   | Clinic email       |
| `phone`     | Text       | Required   | Clinic phone       |
| `logoURL`   | URL / Text | Optional   | Logo image URL     |

**API Calls:**
| Action | API                         |
|--------|-----------------------------|
| List   | `GET /api/clinics/`         |
| Create | `POST /api/clinics/`        |
| Update | `PUT /api/clinics/:id`      |
| Delete | `DELETE /api/clinics/:id`   |

---

### 4.4 Consultations

**Purpose:** Core clinical workflow — view, start, and manage consultations.

#### 4.4.1 Consultation List

```
┌──────────────────────────────────────────────────────────┐
│  Consultations                 [ + Start Consultation ]  │
├──────────────────────────────────────────────────────────┤
│  [🔄 In Progress] [✅ Completed] [📋 All]    🔍 Search   │
├──────────────────────────────────────────────────────────┤
│  TABLE VIEW                                              │
│  ──────────────────────────────────────────────────────  │
│  Patient       │ Health ID  │ Date       │ Status │ Act  │
│  ──────────────────────────────────────────────────────  │
│  John Doe      │ HLTH-123  │ Mar 15     │ 🔄     │ →   │
│  Jane Smith    │ HLTH-456  │ Mar 14     │ ✅     │ →   │
│  ──────────────────────────────────────────────────────  │
└──────────────────────────────────────────────────────────┘
```

**Filter Tabs:** In Progress / Completed / All (client-side filter)

**API Call:** `GET /api/doctors/consultations`

#### 4.4.2 Start New Consultation

Opens a modal:

| Field        | Input Type | Validation             |
|--------------|------------|------------------------|
| `patient_id` | Text       | Required, valid UUID   |

> ⚠️ The doctor must already have an active access permission from the patient. If not, a `403 FORBIDDEN` error will be returned.

**API Call:** `POST /api/consultations/`

#### 4.4.3 Consultation Detail Page

Route: `/doctor/consultations/:consultationId`

```
┌──────────────────────────────────────────────────────────┐
│  ← Back to Consultations                                 │
│                                                          │
│  Consultation #{short_id}                                │
│  Patient: John Doe · HLTH-12345                          │
│  Date: March 15, 2026                                    │
│  Status: [🔄 In Progress ▼]                               │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📋 Prescription                                         │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Drug Name    │ Dosage │ Frequency  │ Days       │    │
│  │  ──────────────────────────────────────────────  │    │
│  │  Metformin    │ 500mg  │ 2x daily   │ 30         │    │
│  │  Lisinopril   │ 10mg   │ 1x daily   │ 60         │    │
│  │  ──────────────────────────────────────────────  │    │
│  │  [ ✏️ Edit Prescription ]                        │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  OR if no prescription:                                  │
│  ┌──────────────────────────────────────────────────┐    │
│  │  No prescription yet.                             │    │
│  │  [ + Create Prescription ]                        │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Status Updater:**
- Dropdown or toggle to change status
- Options: `in_progress`, `completed`
- Changing to `completed` triggers a confirmation modal: "Mark this consultation as completed? You won't be able to modify the prescription afterward."

**API Calls:**
| Action               | API                                                    |
|----------------------|--------------------------------------------------------|
| Load Consultation    | `GET /api/consultations/:consultationId`               |
| Update Status        | `PUT /api/consultations/:consultationId/status`        |
| Load Prescription    | `GET /api/consultations/:consultationId/prescription`  |

#### 4.4.4 Prescription Editor

Opens as a **full-width modal** or **inline expandable section**.

```
┌──────────────────────────────────────────────────────────┐
│  Prescription Editor                                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┬────────┬───────────┬──────────┬────┐   │
│  │ Drug Name   │ Dosage │ Frequency │ Duration │ ✕  │   │
│  ├─────────────┼────────┼───────────┼──────────┼────┤   │
│  │ [Metformin ]│ [500mg]│ [2x daily]│ [30 days]│ 🗑️ │   │
│  │ [Lisinopril]│ [10mg ]│ [1x daily]│ [60 days]│ 🗑️ │   │
│  │ [          ]│ [     ]│ [        ]│ [       ]│ 🗑️ │   │
│  └─────────────┴────────┴───────────┴──────────┴────┘   │
│                                                          │
│  [ + Add Another Drug ]                                  │
│                                                          │
│  ────────────────────────────────────────────────────    │
│                      [ Cancel ]  [ 💾 Save Prescription ] │
└──────────────────────────────────────────────────────────┘
```

**Each Row:**

| Field           | Input Type | Validation                 |
|-----------------|------------|----------------------------|
| `drug_name`     | Text       | Required                   |
| `dosage`        | Text       | Required (e.g. "500mg")    |
| `frequency`     | Text       | Required (e.g. "2x daily") |
| `duration_days` | Number     | Required, positive integer |

**Behavior:**
- Start with 1 empty row, add more with "+ Add Another Drug"
- Remove rows with the trash icon (at least 1 must remain)
- On save, the entire `items` array is sent — this **replaces** the existing prescription

> ⚠️ Disabled for `completed` consultations — show a notice: "This consultation is completed. Prescriptions can no longer be modified."

**API Call:** `POST /api/consultations/:consultationId/prescription`

---

### 4.5 Active Medications Manager

**Purpose:** Manage active medications for patients.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  Active Medications                  [ + Add Medication ] │
├──────────────────────────────────────────────────────────┤
│  🔍 Search Patient by User ID: [________________] [Go]   │
├──────────────────────────────────────────────────────────┤
│  Patient: John Doe (user-uuid)                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  💊 Metformin · 500mg                            │    │
│  │  For: Diabetes · Prescribed: Jan 1, 2026         │    │
│  │  By: You                             ✏️  🗑️     │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  💊 Lisinopril · 10mg                            │    │
│  │  For: Hypertension · Prescribed: Feb 14, 2026    │    │
│  │  By: Dr. Patel                       ✏️  🗑️     │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Add Medication Modal:**

| Field           | Input Type     | Validation        |
|-----------------|----------------|-------------------|
| `user_id`       | Text           | Required, UUID    |
| `name`          | Text           | Required          |
| `dosage`        | Text           | Required          |
| `prescibed_for` | Text           | Required          |
| `prescibed_at`  | Datetime picker| Required          |

> ⚠️ Note the field names `prescibed_for` and `prescibed_at` (matching the backend column names — typo is intentional on the API side, display correctly on the UI as "Prescribed For" and "Prescribed At").

**API Calls:**
| Action | API                           |
|--------|-------------------------------|
| Search | `GET /api/medications/:userId`|
| Create | `POST /api/medications/`      |
| Update | `PUT /api/medications/:id`    |
| Delete | `DELETE /api/medications/:id`  |

---

### 4.6 Emergency Mode

**Purpose:** Rapid access to critical patient data during emergencies. Also triggers email notifications to emergency contacts.

> 🚨 This page should feel **urgent and distinct** — use a subtle red tint on the page background (`--error` at 5% opacity) and larger typography.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  🆘 Emergency Patient Lookup                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Patient ID: [_____________________________]             │
│  Clinic ID:  [_____________________________]             │
│                                                          │
│  [ 🚨 Fetch Emergency Data ]                             │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────── Patient Info ─────────────────────┐   │
│  │  Name: John Doe  ·  Gender: Male  ·  Blood: O+   │   │
│  │  Age: 26 years                                    │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────── Allergies ────────────────────────┐   │
│  │  🥜 Peanuts [SEVERE]  ·  💊 Penicillin [MODERATE] │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────── Chronic Conditions ───────────────┐   │
│  │  Diabetes Type 2 [Managed] · Diagnosed: Jun 2023  │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────── Active Medications ───────────────┐   │
│  │  Metformin 500mg · For: Diabetes · By: Dr. Smith  │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  ✅ Emergency emails sent to patient's contacts          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**API Call:** `GET /api/doctors/emergency/:patientId/:clinicId`

> 📧 **Side Effect:** Emails are automatically sent to emergency contacts. Display a confirmation banner after a successful response.

---

### 4.7 OCR Prescription Scanner

**Purpose:** Upload a prescription image/PDF, extract data via OCR, and save it to the database.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  📸 OCR Prescription Scanner                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │                                                  │    │
│  │      📁 Drop prescription image here             │    │
│  │      or click to browse                          │    │
│  │                                                  │    │
│  │      Accepted: JPEG, PNG, PDF (max 10MB)         │    │
│  │                                                  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  Optional Metadata:                                      │
│  Consultation ID: [_____________________________]        │
│  Patient ID:      [_____________________________]        │
│  Doctor ID:       [_____________________________]        │
│                                                          │
│  [ 🔍 Scan & Save ]                                     │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  (After scan)                                            │
│                                                          │
│  ✅ Prescription saved!                                  │
│  Prescription ID: {uuid}                                 │
│  Drugs detected: {n}                                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Upload Area:**
- Drag-and-drop zone with dashed border (`--beige-200`)
- On hover/drag-over, border becomes solid `--lime-500`, background `--lime-400` at 5%
- Show file preview thumbnail after selection
- Show a progress indicator while the OCR is processing

**Health Check:**
Before showing the scanner, call `GET /api/ocr/health`. If service is not ready, show:
> ⏳ OCR service is initializing. Please wait...

**API Calls:**
| Action       | API                  |
|--------------|----------------------|
| Health check | `GET /api/ocr/health`|
| Upload/Scan  | `POST /api/ocr/scan` (multipart/form-data) |

---

## 5. Verification-Gating Pattern

Many doctor features require `is_verified = true`. The frontend should handle this consistently:

**If NOT verified, the following should be disabled/hidden:**
- Start Consultation
- View Consultations
- All Clinic CRUD
- Emergency Mode

**Show a persistent banner on affected pages:**
> ⏳ Your account is pending verification by admin. Some features are currently unavailable.

**Implementation:** Check `is_verified` from `GET /api/doctors/` on app load and store in global state. Use this to conditionally render UI elements.

---

## 6. UX Guidelines Specific to Doctor UI

1. **Efficiency is paramount** — doctors don't have time for extra clicks. Consultation list → detail → prescription should be minimal steps.
2. **Emergency mode should be unmissable** — always accessible from the sidebar and the dashboard quick actions. The visual treatment should be distinctly urgent.
3. **Prescription editor UX** — dynamic row addition/removal. Validate all fields before save. Show clear feedback when prescription is saved.
4. **Verification gating** — never show a broken/error state to unverified doctors. Instead, show a clear explanation and what they need to do (wait for admin).
5. **OCR scanner** — show progress and be transparent about failures. The OCR service might not be ready — always check health first.
6. **Desktop-first for doctors** — doctors are more likely on desktop/tablet. Optimize for wide layouts with data tables.


# CareLedger — Patient UI Design Document

> Comprehensive frontend design specification for the **Patient Portal**.
> Refer to [FRONTEND_DESIGN_SYSTEM.md](./FRONTEND_DESIGN_SYSTEM.md) for colors, typography, and shared components.

---

## 1. Overview

The Patient Portal is where patients manage their health profile, grant/revoke doctor access, track consultations, and maintain their medical records (allergies, chronic conditions, emergency contacts). The tone is **reassuring, simple, and empowering** — patients should feel in control of their data.

**Role Accent:** Sage Green (`#84CC16`)

---

## 2. Information Architecture

```
Patient Portal
├── Dashboard (Home)
├── My Profile
│   ├── View / Edit Profile
│   └── Account Settings
├── My Health Records
│   ├── Allergies
│   ├── Chronic Conditions
│   └── Active Medications (read-only)
├── Emergency Contacts
├── Consultations
│   └── Consultation Detail (read-only)
├── Doctor Access
│   ├── Granted Access List
│   ├── Grant New Access
│   └── Revoke Access
└── Settings / Logout
```

---

## 3. Sidebar Navigation

| Icon              | Label              | Route                         |
|-------------------|--------------------|-------------------------------|
| `layout-dashboard`| Dashboard          | `/patient/dashboard`          |
| `user`            | My Profile         | `/patient/profile`            |
| `heart-pulse`     | Health Records     | `/patient/health`             |
| `phone-call`      | Emergency Contacts | `/patient/emergency`          |
| `stethoscope`     | Consultations      | `/patient/consultations`      |
| `shield-check`    | Doctor Access      | `/patient/access`             |
| `settings`        | Settings           | `/patient/settings`           |
| `log-out`         | Logout             | *(action)*                    |

---

## 4. Pages

### 4.1 Dashboard

**Purpose:** At-a-glance overview of the patient's health status and recent activity.

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  👋 Welcome back, {full_name}                           │
│  Health ID: {health_id}                                 │
├────────────────┬──────────────┬──────────────────────────┤
│  STAT CARD     │  STAT CARD   │  STAT CARD              │
│  Active        │  Chronic     │  Doctors with           │
│  Allergies     │  Conditions  │  Access                 │
│  count: {n}    │  count: {n}  │  count: {n}             │
├────────────────┴──────────────┴──────────────────────────┤
│                                                         │
│  🕐 Recent Consultations                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Dr. Smith · Cardiology · Mar 15, 2026 · ✅ Done │    │
│  │ Dr. Patel · General    · Mar 10, 2026 · 🔄 In..│    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  💊 Active Medications     (View All →)                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Metformin 500mg · For: Diabetes · Dr. Smith     │    │
│  │ Lisinopril 10mg · For: Hypertension · Dr. Patel │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Stat Cards:**
- Background: `white`, border-left `4px solid --lime-500`
- Display: large number + label underneath
- Subtle hover: slight elevation

**API Calls on Load:**
| API                              | Purpose                     |
|----------------------------------|-----------------------------|
| `GET /api/patients/`             | Fetch profile (name, health_id) |
| `GET /api/patients/allergies`    | Count of allergies          |
| `GET /api/patients/chronic-conditions` | Count of conditions   |
| `GET /api/patients/access-list`  | Count of active doctors     |
| `GET /api/patients/consultations`| Recent consultations list   |
| `GET /api/medications/:userId`   | Active medications          |

---

### 4.2 My Profile

**Purpose:** View and edit patient profile information.

**Layout:** Two-column — left column for the profile card, right column for the edit form.

**Profile Card (left, read-only):**

```
┌──────────────────────────────┐
│  ┌────┐                     │
│  │ 👤 │  John Doe            │
│  └────┘  Health ID: HLTH-123 │
│                              │
│  📅 DOB:    Jan 15, 2000     │
│  ⚥  Gender: Male            │
│  🩸 Blood:  O+               │
│  📧 Email:  john@example.com │
│  📱 Phone:  9876543210       │
│                              │
│  [ ✏️ Edit Profile ]         │
└──────────────────────────────┘
```

**Edit Mode:**
Clicking "Edit Profile" either opens a modal or transforms the card into an editable form:

| Field           | Input Type | Validation                        |
|-----------------|------------|-----------------------------------|
| `full_name`     | Text       | Required                          |
| `date_of_birth` | Date picker| Optional, must be in the past     |
| `gender`        | Dropdown   | Options: Male, Female, Other      |
| `blood_group`   | Dropdown   | Options: A+, A-, B+, B-, AB+, AB-, O+, O- |

**API Calls:**
| Action      | API                       |
|-------------|---------------------------|
| Load        | `GET /api/patients/`      |
| Save        | `PUT /api/patients/`      |

> ⚠️ `health_id` is **read-only** after creation — show it as a disabled field with a lock icon.

---

### 4.3 Health Records — Allergies Tab

**Purpose:** Full CRUD for patient allergies.

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  Allergies                           [ + Add Allergy ]  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │  🥜 Peanuts                  [SEVERE]  ✏️  🗑️   │   │
│  ├──────────────────────────────────────────────────┤   │
│  │  💊 Penicillin               [MODERATE] ✏️  🗑️  │   │
│  ├──────────────────────────────────────────────────┤   │
│  │  🌾 Gluten                   [MILD]    ✏️  🗑️   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Severity Badges:** Use the severity-colored badges from the design system (mild=yellow, moderate=orange, severe=red).

**Add/Edit Allergy Modal:**

| Field      | Input Type | Validation                                    |
|------------|------------|-----------------------------------------------|
| `allergen` | Text       | Required                                      |
| `severity` | Dropdown   | Options: Mild, Moderate, Severe (required)    |

**Delete Confirmation:** Destructive modal — "Are you sure you want to remove this allergy? This action cannot be undone."

**API Calls:**
| Action | API                               |
|--------|-----------------------------------|
| List   | `GET /api/patients/allergies`     |
| Create | `POST /api/patients/allergies`    |
| Update | `PUT /api/patients/allergies/:id` |
| Delete | `DELETE /api/patients/allergies/:id` |

---

### 4.4 Health Records — Chronic Conditions Tab

**Purpose:** Full CRUD for chronic conditions.

**Layout:** Same card-list style as Allergies.

**Each Card Shows:**
- Condition name (e.g., "Diabetes Type 2")
- Status badge: `Active` (green), `Managed` (blue), `Resolved` (gray)
- Diagnosed date (formatted as "Jun 2023")
- Edit and Delete action icons

**Add/Edit Modal:**

| Field            | Input Type  | Validation                                   |
|------------------|-------------|----------------------------------------------|
| `condition_name` | Text        | Required                                     |
| `status`         | Dropdown    | Options: Active, Managed, Resolved (required)|
| `diagnosed_date` | Date picker | Optional                                     |

**API Calls:**
| Action | API                                        |
|--------|--------------------------------------------|
| List   | `GET /api/patients/chronic-conditions`     |
| Create | `POST /api/patients/chronic-conditions`    |
| Update | `PUT /api/patients/chronic-conditions/:id` |
| Delete | `DELETE /api/patients/chronic-conditions/:id` |

---

### 4.5 Health Records — Active Medications Tab

**Purpose:** Read-only view of medications prescribed by doctors.

> ⚠️ Patients **cannot** add, edit, or delete medications — only doctors can. This should be clearly communicated with a notice banner.

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  Active Medications                                     │
│  ℹ️  Medications are managed by your doctor             │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │  💊 Metformin                                    │   │
│  │  Dosage: 500mg                                   │   │
│  │  For: Diabetes · Prescribed: Jan 1, 2026         │   │
│  ├──────────────────────────────────────────────────┤   │
│  │  💊 Lisinopril                                   │   │
│  │  Dosage: 10mg                                    │   │
│  │  For: Hypertension · Prescribed: Feb 14, 2026    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**API Call:** `GET /api/medications/:userId` (use the authenticated user's ID)

---

### 4.6 Emergency Contacts

**Purpose:** Full CRUD for emergency contacts.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  Emergency Contacts                  [ + Add Contact ]   │
├──────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────┐   │
│  │  👤 Jane Doe                                      │   │
│  │  📱 1111111111 · 📧 jane@example.com              │   │
│  │  Relationship: Spouse                    ✏️  🗑️   │   │
│  ├───────────────────────────────────────────────────┤   │
│  │  👤 Robert Doe                                    │   │
│  │  📱 2222222222 · 📧 robert@example.com            │   │
│  │  Relationship: Father                   ✏️  🗑️    │   │
│  └───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

**Add/Edit Modal:**

| Field                  | Input Type | Validation          |
|------------------------|------------|---------------------|
| `contact_name`         | Text       | Required            |
| `contact_phone`        | Text       | Required            |
| `contact_email`        | Email      | Required            |
| `contact_relationship` | Text       | Optional            |

**API Calls:**
| Action | API                                        |
|--------|--------------------------------------------|
| List   | `GET /api/patients/emergency-info`         |
| Create | `POST /api/patients/emergency-info`        |
| Update | `PUT /api/patients/emergency-info/:id`     |
| Delete | `DELETE /api/patients/emergency-info/:id`  |

---

### 4.7 Consultations

**Purpose:** Read-only list of all consultations the patient has had/is having.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  My Consultations                                        │
├──────────────────────────────────────────────────────────┤
│  🔍 [Search by doctor name...]    [Filter: All ▼]       │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐    │
│  │  🩺 Dr. Smith                                    │    │
│  │  Cardiology · Heart Care Center                  │    │
│  │  📅 Mar 15, 2026             [✅ Completed]      │    │
│  │                              [ View Details → ]  │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  🩺 Dr. Patel                                    │    │
│  │  General · City Clinic                           │    │
│  │  📅 Mar 10, 2026             [🔄 In Progress]    │    │
│  │                              [ View Details → ]  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Status Badges:**
- `in_progress` → `🔄 In Progress` (warning badge)
- `completed` → `✅ Completed` (success badge)

**Filter Dropdown:** All / In Progress / Completed (client-side filter)

**API Call:** `GET /api/patients/consultations`

> Consultation detail page is optional — the list view already contains all the information returned by the API (doctor name, specialization, clinic, date, status).

---

### 4.8 Doctor Access Management

**Purpose:** Manage which doctors can view the patient's health data.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  Doctor Access                    [ + Grant Access ]     │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐    │
│  │  🩺 Dr. Smith · Cardiology                       │    │
│  │  Heart Care Center                               │    │
│  │  Status: [ACTIVE]  · Granted: Mar 1, 2026        │    │
│  │  Expires: Never                                  │    │
│  │                           [ 🔴 Revoke Access ]   │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  🩺 Dr. Patel · General                          │    │
│  │  City Clinic                                     │    │
│  │  Status: [REVOKED] · Granted: Jan 15, 2026       │    │
│  │                                                  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Status Badges:**
- `ACTIVE` → green badge
- `REVOKED` → red badge

**Grant Access Modal:**

| Field       | Input Type  | Validation                           |
|-------------|-------------|--------------------------------------|
| `doctor_id` | Text / Search | Required, valid UUID (doctor profile ID) |
| `expires_at`| Datetime picker | Optional (null = no expiry)      |

> 💡 **UX Improvement Suggestion:** Rather than asking the patient to enter a UUID, consider a doctor search field that looks up doctors by name (would require a new search endpoint). For now, the patient needs to know the doctor's profile ID.

**Revoke Confirmation:** Destructive modal — "Revoke Dr. Smith's access to your health records?"

**API Calls:**
| Action       | API                                            |
|--------------|------------------------------------------------|
| List         | `GET /api/patients/access-list`                |
| Grant        | `POST /api/patients/grant-access`              |
| Revoke       | `DELETE /api/patients/revoke-access/:doctorId`  |

---

### 4.9 Account Settings

**Purpose:** Update email, phone, or password.

**Layout:** Simple form:

| Field            | Input Type | Notes                        |
|------------------|------------|------------------------------|
| `email`          | Email      | Pre-filled with current      |
| `phone`          | Text       | Pre-filled with current      |
| `plain_password` | Password   | Blank (only fill to change)  |
| Confirm Password | Password   | Client-side validation only  |

**API Call:** `PUT /api/users/:id` (use the authenticated user's ID from JWT)

---

## 5. UX Guidelines Specific to Patient UI

1. **Health data is sensitive** — always confirm before deleting anything (allergies, conditions, emergency contacts, access permissions).
2. **Medications are read-only** — make this crystal clear with a notice banner and disabled action buttons. Don't confuse patients into thinking they can self-prescribe.
3. **Access management is critical** — use visual cues (green/red badges, expiry dates) to help patients quickly see who has access. The Revoke button should be clearly destructive-styled.
4. **Empty states matter** — a new patient with no data should see friendly empty states with CTAs to add their first allergy, condition, or emergency contact. Don't show an empty table.
5. **Dashboard is the heartbeat** — it should load fast and give a meaningful snapshot. Use skeleton loaders while the multiple API calls resolve.
6. **Mobile-first for patients** — patients are most likely on mobile devices. Ensure all layouts fold gracefully to single-column on small screens.


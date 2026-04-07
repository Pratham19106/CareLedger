# CareLedger — Admin UI Design Document

> Comprehensive frontend design specification for the **Admin Panel**.
> Refer to [FRONTEND_DESIGN_SYSTEM.md](./FRONTEND_DESIGN_SYSTEM.md) for colors, typography, and shared components.

---

## 1. Overview

The Admin Panel is a management dashboard for platform administrators. The primary function is **doctor verification** and **user management**. The tone is **authoritative, clean, and data-centric** — the admin needs clear visibility into the platform's users and pending actions.

**Role Accent:** Warm Amber (`#F59E0B`)

---

## 2. Information Architecture

```
Admin Panel
├── Dashboard (Home)
│   ├── Platform Stats
│   └── Pending Verifications
├── User Management
│   ├── All Users (filterable by role)
│   ├── User Detail
│   ├── Edit User
│   └── Delete User
├── Doctor Verification
│   ├── Pending Doctors
│   └── Verify Doctor
└── Settings / Logout
```

> The admin interface is intentionally lean — it only has access to user management and doctor verification. It does not have direct access to clinical data (consultations, prescriptions, patient health records).

---

## 3. Sidebar Navigation

| Icon              | Label                | Route                         |
|-------------------|----------------------|-------------------------------|
| `layout-dashboard`| Dashboard            | `/admin/dashboard`            |
| `users`           | User Management      | `/admin/users`                |
| `check-circle`    | Doctor Verification  | `/admin/verify`               |
| `settings`        | Settings             | `/admin/settings`             |
| `log-out`         | Logout               | *(action)*                    |

The sidebar is shorter than the other portals — this is intentional. Admins have fewer but higher-privilege features.

---

## 4. Pages

### 4.1 Dashboard

**Purpose:** High-level platform overview and action center for pending tasks.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  🛡️ Admin Dashboard                                     │
│  Welcome back, Admin                                     │
├──────────────┬──────────────┬────────────────────────────┤
│  STAT CARD   │  STAT CARD   │  STAT CARD                │
│  Total       │  Total       │  Total                    │
│  Users       │  Patients    │  Doctors                  │
│  count: {n}  │  count: {n}  │  count: {n}               │
├──────────────┴──────────────┴────────────────────────────┤
│                                                          │
│  ⚠️ Pending Doctor Verifications ({count})              │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Dr. New Doctor · MED-789 · Neurology            │    │
│  │  Registered: Mar 30, 2026        [ ✅ Verify ]   │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  Dr. Another · MED-456 · Orthopedics             │    │
│  │  Registered: Mar 29, 2026        [ ✅ Verify ]   │    │
│  └──────────────────────────────────────────────────┘    │
│                         [ View All Pending → ]           │
│                                                          │
│  📊 Recent Registrations                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │ john@example.com · patient · Mar 31, 2026        │    │
│  │ drsmith@example.com · doctor · Mar 30, 2026      │    │
│  │ jane@example.com · patient · Mar 29, 2026        │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Stat Cards:**
- Background: `white`, border-top `4px solid --warning`
- Large number prominent, label below in muted text
- Quick visual of platform health

**API Calls on Load:**
| API                                      | Purpose                    |
|------------------------------------------|----------------------------|
| `GET /api/users/`                        | All users (count totals)   |
| `GET /api/users/?role=patient`           | Patient count              |
| `GET /api/users/?role=doctor`            | Doctor count               |

> **Pending Verifications:** There is no dedicated API to list unverified doctors. The admin frontend should fetch all users with `role=doctor`, then for each doctor user, call `GET /api/doctors/:id` — or better, the admin can visually identify unverified doctors from the user list. This is a limitation of the current API.
>
> **💡 Recommended API Enhancement:** Add a `GET /api/admin/doctors/pending` endpoint that returns all unverified doctors. This would simplify the admin dashboard significantly.

---

### 4.2 User Management

**Purpose:** View, filter, edit, and delete all platform users.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  User Management                                         │
├──────────────────────────────────────────────────────────┤
│  [All] [Patients] [Doctors] [Admins]    🔍 Search email  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  TABLE                                                   │
│  ──────────────────────────────────────────────────────  │
│  Email           │ Phone      │ Role    │ Created   │ ⚙️ │
│  ──────────────────────────────────────────────────────  │
│  john@ex.com     │ 9876543210 │ patient │ Mar 31    │ ⚙️ │
│  drsmith@ex.com  │ 9999999999 │ doctor  │ Mar 30    │ ⚙️ │
│  jane@ex.com     │ 1111111111 │ patient │ Mar 29    │ ⚙️ │
│  admin@ex.com    │ 0000000000 │ admin   │ Jan 01    │ ⚙️ │
│  ──────────────────────────────────────────────────────  │
│                                                          │
│  Showing 1-10 of {total}     < Prev  1  2  3  Next >    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Role Filter Tabs:**
- `All` — no filter
- `Patients` — `?role=patient`
- `Doctors` — `?role=doctor`
- `Admins` — `?role=admin`
- Active tab highlighted with `--warning` accent

**Role Badges:**
| Role    | Badge Color                   |
|---------|-------------------------------|
| patient | `--lime-400` @ 20%, `--lime-800` text |
| doctor  | Teal @ 20%, teal-800 text     |
| admin   | `--warning` @ 20%, amber-800 text |

**Action Menu (⚙️):** Dropdown with:
- 👁️ View Details
- ✏️ Edit User
- 🗑️ Delete User (destructive, with confirmation)

**Search:** Client-side filter by email substring.

**Pagination:** Client-side (since the API returns all users). Show 10-20 per page.

**API Calls:**
| Action          | API                                |
|-----------------|------------------------------------|
| Load All        | `GET /api/users/`                  |
| Filter by Role  | `GET /api/users/?role={role}`      |

---

### 4.3 User Detail / Edit

**Purpose:** View or edit a specific user's account details.

Route: `/admin/users/:id`

**Layout:**

```
┌──────────────────────────────────┐
│  ← Back to Users                │
│                                  │
│  User Details                    │
│  ┌──────────────────────────────┐│
│  │  ID:    {uuid}               ││
│  │  Email: john@example.com     ││
│  │  Phone: 9876543210           ││
│  │  Role:  [patient]            ││
│  │  Created: Mar 31, 2026       ││
│  └──────────────────────────────┘│
│                                  │
│  [ ✏️ Edit ] [ 🗑️ Delete User ] │
│                                  │
└──────────────────────────────────┘
```

**Edit Modal:**

| Field            | Input Type | Validation             | Notes               |
|------------------|------------|------------------------|----------------------|
| `email`          | Email      | Optional               | Pre-filled           |
| `phone`          | Text       | Optional               | Pre-filled           |
| `plain_password` | Password   | Optional               | Leave blank to skip  |

> ⚠️ Role and user ID are **not editable**. `created_at` is display-only.

**Delete Confirmation:** High-severity destructive modal:
> "⚠️ Permanently delete user **john@example.com**? This action cannot be undone and will remove all associated data."

Two-step confirmation: Type `DELETE` to confirm.

**API Calls:**
| Action | API                        |
|--------|----------------------------|
| Load   | `GET /api/users/:id`       |
| Update | `PUT /api/users/:id`       |
| Delete | `DELETE /api/users/:id`    |

---

### 4.4 Doctor Verification

**Purpose:** View and verify unverified doctor accounts.

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  Doctor Verification                                     │
├──────────────────────────────────────────────────────────┤
│  [⏳ Pending] [✅ Verified] [All]                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  🩺 Dr. New Doctor                               │    │
│  │  License: MED-789012                             │    │
│  │  Specialization: Neurology                       │    │
│  │  Status: [⏳ Pending Verification]                │    │
│  │  Registered: March 30, 2026                      │    │
│  │                                                  │    │
│  │  [ ✅ Verify Doctor ]                            │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  🩺 Dr. Another                                  │    │
│  │  License: MED-456789                             │    │
│  │  Specialization: Orthopedics                     │    │
│  │  Status: [⏳ Pending Verification]                │    │
│  │  Registered: March 29, 2026                      │    │
│  │                                                  │    │
│  │  [ ✅ Verify Doctor ]                            │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  🩺 Dr. Smith                                    │    │
│  │  License: MED-123456                             │    │
│  │  Specialization: Cardiology                      │    │
│  │  Status: [✅ Verified]                            │    │
│  │  (verified indicator, no action button)           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Verify Confirmation Modal:**
> "Verify **Dr. New Doctor** (License: MED-789012)?
> This will grant them access to clinical features including consultations, prescriptions, and emergency patient data."
>
> [ Cancel ] [ ✅ Confirm Verification ]

**Status Badges:**
- `Pending` → amber badge with clock icon
- `Verified` → green badge with check icon

**API Flow:**
1. Fetch all doctor users: `GET /api/users/?role=doctor`
2. For each doctor user, fetch their doctor profile: `GET /api/doctors/:id` (using the user ID to look up)
3. Display with verification status
4. To verify: `PUT /api/admin/doctors/:doctorId/verify`

> **Important:** The verification API uses the **doctor profile ID** (from the `doctors` table), NOT the user ID. The admin must first resolve the doctor profile ID from the user list.

> **💡 Recommended API Enhancement:** Consider adding a `GET /api/admin/doctors` endpoint that returns all doctor profiles with their user info and verification status in a single call. This would eliminate the N+1 query problem on the admin frontend.

---

### 4.5 Admin Settings / Account

**Purpose:** Update admin's own account credentials.

Same as the settings page for other roles:

| Field            | Input Type | Notes                        |
|------------------|------------|------------------------------|
| `email`          | Email      | Pre-filled with current      |
| `phone`          | Text       | Pre-filled with current      |
| `plain_password` | Password   | Leave blank to skip          |

**API Call:** `PUT /api/users/:id`

---

## 5. Key Considerations for Admin UI

### 5.1 Current API Limitations

The admin API is currently minimal. Here's what the frontend needs to work around:

| Feature Needed                  | Current API Status                      | Workaround                                    |
|----------------------------------|-----------------------------------------|-----------------------------------------------|
| List unverified doctors          | No dedicated endpoint                   | Fetch all doctors + check `is_verified`        |
| Doctor profile from user ID      | No direct mapping endpoint              | Use `GET /api/doctors/:id` per doctor user     |
| User count by role               | Must fetch all users                    | Client-side filtering from `GET /api/users/`   |
| Audit logs                       | Not available                           | Not implementable with current API             |

### 5.2 Security Notes

- Admin accounts **cannot be created via signup** (`role` must be `patient` or `doctor`). Admin users must be seeded directly in the database.
- All admin API calls require both `authenticate` and `requireAdmin` middleware.
- The admin can delete **any** user — this is a powerful action. The UI should reflect this gravity with multi-step confirmation.

### 5.3 Future Feature Suggestions

These are features the admin UI **could** support with API additions:

| Feature                    | Description                                                  |
|---------------------------|--------------------------------------------------------------|
| Revoke doctor verification | Ability to un-verify a doctor (not currently in API)         |
| Dashboard analytics        | Charts for user growth, consultation volume, etc.            |
| Audit trail                | Log of all admin actions (verifications, deletions)          |
| Bulk actions               | Select multiple users for batch operations                   |
| Doctor detail view         | See a doctor's consultations, clinics, and patient access    |
| System health              | OCR service status, database connection pool stats           |

---

## 6. UX Guidelines Specific to Admin UI

1. **Power with caution** — every admin action has significant impact. Use confirmation modals generously, especially for deletions and verifications.
2. **Verification is the primary job** — the dashboard should prominently surface pending verifications. If there are 0 pending, show a "All caught up! 🎉" state.
3. **Data density is acceptable** — admins are power users. Tables with more columns are fine. Avoid oversimplifying the data display.
4. **Search and filter are essential** — with potentially hundreds of users, the admin must be able to quickly find specific users by email, role, or registration date.
5. **Desktop-only is acceptable** — admin panels are almost exclusively used on desktop. Mobile optimization is low priority.
6. **Clear role identification** — always show role badges prominently so the admin can quickly distinguish patients from doctors from other admins.


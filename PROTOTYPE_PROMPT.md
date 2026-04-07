# Prompt for AI Agent — CareLedger Frontend Prototype

> Copy everything below and paste it as your prompt. Attach the 4 design documents alongside this prompt.

---

## Attached Files

The following 4 files are attached to this prompt. Read them thoroughly before starting:

1. **FRONTEND_DESIGN_SYSTEM.md** — Shared design system (color palette, typography, spacing, components, layout, auth flow, animations, icons)
2. **FRONTEND_PATIENT_UI.md** — Patient portal design specification (9 pages with wireframes and API mappings)
3. **FRONTEND_DOCTOR_UI.md** — Doctor portal design specification (7 pages with wireframes, prescription editor, emergency mode, OCR)
4. **FRONTEND_ADMIN_UI.md** — Admin panel design specification (5 pages with user management and doctor verification)

---

## Prompt

Build a **fully functional, visually polished frontend prototype** for a healthcare platform called **CareLedger** based on the 4 attached design documents.

### What to Build

A single-page web application (SPA) with **three separate portals** accessible via role-based login:

1. **Patient Portal** — Health profile management, allergies, chronic conditions, emergency contacts, consultation history, doctor access control
2. **Doctor Portal** — Clinical workspace with consultations, prescription management, clinic management, medication management, emergency patient lookup, OCR scanner interface
3. **Admin Panel** — User management dashboard, doctor verification workflow

### Tech Stack

- **React** (with Vite as the build tool)
- **React Router** for client-side routing
- **Tailwind css**
- **Lucide React** for icons (`lucide-react` package)
- **Google Fonts: Inter** for typography

### Critical Design Requirements

Follow the design system document **exactly** for these:

#### Color Palette
- **Primary colors:** Beige (`#FDF8F0` to `#C2A875`) for backgrounds/surfaces and Lime Green (`#A3E635` to `#3F6212`) for actions/CTAs
- **Neutral colors:** Stone scale (`#FAFAF9` to `#1C1917`) for text and borders
- **Semantic colors:** Success green `#22C55E`, Warning amber `#F59E0B`, Error red `#EF4444`, Info blue `#3B82F6`
- **Role accent colors:** Patient = Sage Green `#84CC16`, Doctor = Teal `#14B8A6`, Admin = Warm Amber `#F59E0B`

#### Typography
- Font: **Inter** (import from Google Fonts)
- Page titles: 28px/700, Section titles: 22px/600, Body: 15px/400, Small: 13px/400

#### Layout Shell
All three portals share the same layout structure:
- **Top bar** (64px height, `--beige-50` background, logo left, user avatar right)
- **Sidebar** (260px width, white background, collapsible to 72px icon-only, nav items with role accent color for active state)
- **Main content area** (`--beige-50` background, max-width 1200px, centered, padded)

### Data & API Simulation

Since this is a **prototype** (no real backend), use **mock data** with the following approach:

1. **Create a `mockData.js` file** with realistic sample data for:
   - 3-4 users (1 patient, 2 doctors, 1 admin) with pre-set credentials
   - 1 patient profile with full health data (allergies, chronic conditions, emergency contacts, medications)
   - 2 doctor profiles (1 verified, 1 unverified) with clinics and consultations
   - Several consultations with prescriptions
   - Access permissions between patient and doctors

2. **Create a mock API service layer** (`mockApi.js`) that simulates API calls with:
   - `async` functions that return promises (use `setTimeout` for 300-500ms fake latency)
   - Proper success/error response envelopes matching the format:
     ```json
     { "success": true, "data": {...}, "message": "..." }
     { "success": false, "error": { "code": "...", "message": "..." } }
     ```
   - CRUD operations that update an in-memory store (so changes persist during the session)

3. **Hardcode login credentials** for easy testing:
   - Patient: `patient@test.com` / `password123` / role: `patient`
   - Doctor (verified): `doctor@test.com` / `password123` / role: `doctor`
   - Doctor (unverified): `newdoc@test.com` / `password123` / role: `doctor`
   - Admin: `admin@test.com` / `password123` / role: `admin`

4. **Store auth state** in React context. Generate a fake JWT-like token on login. Use it for role-based route protection.

### Pages to Implement

#### Shared Pages
- **Login page** — Role selector tabs (Patient/Doctor/Admin), email + password fields, centered card on beige gradient background, lime green login button
- **Signup page** — Same layout as login, additional fields (email, phone, password, confirm password, role selector limited to Patient/Doctor)

#### Patient Portal (route: `/patient/*`)
Implement ALL of these pages with full interactivity:
- **Dashboard** — Welcome message, stat cards (allergy count, condition count, doctor access count), recent consultations list, active medications summary
- **My Profile** — View profile card + edit mode (modal or inline form) for name, DOB, gender, blood group. Health ID shown as read-only
- **Allergies** — Card list with severity badges (mild=yellow, moderate=orange, severe=red). Add/edit modal with allergen + severity dropdown. Delete with confirmation
- **Chronic Conditions** — Card list with status badges (active=green, managed=blue, resolved=gray). Add/edit modal. Delete with confirmation
- **Active Medications** — Read-only list with info banner "Medications are managed by your doctor". Each card shows drug name, dosage, prescribed for, date
- **Emergency Contacts** — Card list with name, phone, email, relationship. Full CRUD via modals
- **Consultations** — Card list with doctor name, specialization, clinic, date, status badges. Filter tabs (All/In Progress/Completed)
- **Doctor Access** — Card list showing granted doctors with status badges (ACTIVE=green, REVOKED=red). Grant access modal. Revoke with confirmation
- **Settings** — Update email, phone, password form

#### Doctor Portal (route: `/doctor/*`)
- **Dashboard** — Welcome + verification status banner (if unverified: amber warning banner). Stat cards, recent consultations, quick action buttons
- **My Profile** — View card + edit modal for name, specialization. License and verification status read-only
- **My Clinics** — Card list for clinics with name, address, email, phone. Full CRUD via modals
- **Consultations** — Table/card list with filter tabs. "Start Consultation" modal. Click into consultation detail page
- **Consultation Detail** — Shows patient info, status dropdown (with confirmation for marking complete), prescription section (view or create/edit)
- **Prescription Editor** — Dynamic row-based editor. Add rows, remove rows, fields: drug name, dosage, frequency, duration days. Save replaces all items. Disabled for completed consultations
- **Medications** — Search by patient user ID, then show medications. Add/edit/delete medications
- **Emergency Mode** — Distinct visual treatment (subtle red tint). Patient ID + Clinic ID inputs. Shows comprehensive patient data (allergies, conditions, medications). "Emails sent" confirmation
- **OCR Scanner** — Drag-and-drop upload zone, file preview, optional metadata fields, scan button, result display. Health status check indicator
- **Settings** — Same as patient

#### Admin Panel (route: `/admin/*`)
- **Dashboard** — Stat cards (total users, patients, doctors). Pending verifications list with verify buttons. Recent registrations
- **User Management** — Table with all users. Role filter tabs. Search by email. Action dropdown per row (view, edit, delete)
- **User Detail/Edit** — View user card, edit modal (email, phone, password), delete with two-step confirmation (type "DELETE")
- **Doctor Verification** — Card list of doctors with verification status. Filter tabs (Pending/Verified/All). Verify button with confirmation modal
- **Settings** — Same as others

### Component Requirements

Build these as reusable React components following the design system exactly:

- `<Button variant="primary|secondary|destructive|ghost" size="sm|md|lg">` — All button styles from the design system
- `<Input>` / `<Select>` / `<DatePicker>` — Styled form fields with labels, error states, focus rings
- `<Card>` — White card with beige border, shadow, hover elevation
- `<Badge variant="active|pending|completed|revoked|info|severity-mild|severity-moderate|severity-severe">` — All badge styles
- `<Modal>` — Backdrop blur overlay, white dialog, title + actions
- `<Toast>` — Slide-in from top-right, auto-dismiss, colored left border
- `<Table>` — Styled table with header, alternating rows, hover
- `<Sidebar>` — Collapsible with icon+label nav items, role accent active indicator
- `<TopBar>` — Logo, role badge, user dropdown
- `<EmptyState>` — Centered message with icon and optional CTA
- `<SkeletonLoader>` — Animated shimmer placeholders
- `<StatCard>` — Number + label with colored left border
- `<ConfirmDialog>` — Destructive confirmation with typed confirmation for critical actions

### Interaction & Animation Requirements

- **Button hover:** Background darkens one shade, 150ms ease
- **Card hover:** Shadow elevates, 200ms ease
- **Modal appear:** Overlay fades in 200ms, dialog scales from 0.95→1 in 200ms
- **Toast:** Slides in from right in 300ms, auto-dismisses after 5 seconds
- **Sidebar collapse:** Width transition 250ms ease-in-out
- **Page transitions:** Content fade 150ms
- **Skeleton loading:** Animated shimmer gradient sweep 1.5s infinite
- **Focus rings:** 3px offset ring in lime-400 at 40% opacity

### Quality Bar

This prototype should look like a **polished, production-ready application**, not a wireframe or MVP. Specific requirements:

1. **Every page must have realistic mock data populated** — no empty placeholder text
2. **All CRUD operations must work within the session** — add an allergy, it shows up; delete a user, they disappear
3. **Role-based routing must work** — patient can't access doctor routes and vice versa
4. **Responsive design** — must work on desktop (≥1024px) and gracefully degrade on tablet (768-1023px, collapsed sidebar) and mobile (<768px, hamburger menu)
5. **Loading states** — show skeleton loaders before mock data "loads"
6. **Empty states** — show friendly empty state components with CTAs when a list is empty
7. **Error handling** — show toast notifications for all operations (success and error)
8. **Form validation** — validate required fields, show inline errors, disable submit until valid
9. **The design should feel premium** — smooth animations, consistent spacing, harmonious colors, clean typography
10. **Unverified doctor gating** — when logged in as the unverified doctor, consultation/clinic/emergency features should show the warning banner and be disabled

### File Structure

Organize the project like this:

```
src/
├── assets/
│   └── logo.svg
├── components/
│   ├── shared/          # Button, Card, Modal, Toast, etc.
│   ├── layout/          # TopBar, Sidebar, AppLayout
│   └── forms/           # Input, Select, DatePicker, etc.
├── pages/
│   ├── auth/            # Login, Signup
│   ├── patient/         # All patient pages
│   ├── doctor/          # All doctor pages
│   └── admin/           # All admin pages
├── context/
│   ├── AuthContext.jsx
│   └── ToastContext.jsx
├── services/
│   ├── mockData.js      # All mock data
│   └── mockApi.js       # Mock API service layer
├── styles/
│   ├── variables.css    # All CSS custom properties (design tokens)
│   ├── global.css       # Global styles, resets, typography
│   └── components/      # Per-component CSS files
├── utils/
│   └── helpers.js       # Formatters, validators
├── App.jsx
├── main.jsx
└── index.css
```

### How to Start

1. Initialize the project: `npx -y create-vite@latest ./ -- --template react`
2. Install dependencies: `npm install react-router-dom lucide-react`
3. Set up CSS variables file first with all design tokens from `FRONTEND_DESIGN_SYSTEM.md`
4. Build shared components before pages
5. Implement auth flow first (login → routing → protected routes)
6. Build pages per portal, starting with Patient (most complex), then Doctor, then Admin
7. Run with `npm run dev`

---

**IMPORTANT:** Read all 4 attached design documents completely before writing any code. The documents contain exact specifications for every page, every component, every color, every interaction. Follow them precisely.

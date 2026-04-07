# CareLedger — Design System & Shared UI Guidelines

> This document defines the visual identity, component library, and shared patterns used across **all three** interfaces: Patient, Doctor, and Admin.

---

## 1. Brand Identity

**CareLedger** is a health-data management platform. The visual language should communicate **trust, cleanliness, and approachability** — not clinical coldness.

**Design Philosophy:** *Warm clinical* — blend the precision of a medical interface with the warmth of a modern lifestyle app.

---

## 2. Color Palette

The primary palette uses **beige** (warmth, approachability) and **lime green** (health, vitality, growth). Accents and semantic colors extend the system.

### Primary Colors

| Token               | Hex       | Usage                                     |
|----------------------|-----------|-------------------------------------------|
| `--beige-50`         | `#FDF8F0` | Page backgrounds, light surfaces          |
| `--beige-100`        | `#F5ECDB` | Card backgrounds, hover states            |
| `--beige-200`        | `#EAD9B8` | Borders, dividers, subtle accents         |
| `--beige-300`        | `#D4BF96` | Secondary text, muted elements            |
| `--beige-400`        | `#C2A875` | Placeholder text                          |
| `--lime-400`         | `#A3E635` | Highlights, progress bars, active accents |
| `--lime-500`         | `#84CC16` | **Primary action buttons**, CTA           |
| `--lime-600`         | `#65A30D` | Hover state on primary buttons            |
| `--lime-700`         | `#4D7C0F` | Active/pressed state, focus rings         |
| `--lime-800`         | `#3F6212` | Primary button text (dark on light)       |

### Neutral Colors

| Token               | Hex       | Usage                                     |
|----------------------|-----------|-------------------------------------------|
| `--stone-50`         | `#FAFAF9` | Alternate card backgrounds                |
| `--stone-100`        | `#F5F5F4` | Input fields, table striping              |
| `--stone-200`        | `#E7E5E4` | Borders                                   |
| `--stone-500`        | `#78716C` | Secondary text                            |
| `--stone-700`        | `#44403C` | Primary body text                         |
| `--stone-900`        | `#1C1917` | Headings, critical text                   |

### Semantic Colors

| Token               | Hex       | Usage                                     |
|----------------------|-----------|-------------------------------------------|
| `--success`          | `#22C55E` | Success messages, verified badges         |
| `--warning`          | `#F59E0B` | Warnings, pending states                  |
| `--error`            | `#EF4444` | Error messages, destructive actions       |
| `--info`             | `#3B82F6` | Informational alerts, links               |

### Role Accent Colors

Each user role gets a subtle accent color for its interface header/sidebar to provide wayfinding:

| Role    | Accent          | Hex       | Application                    |
|---------|-----------------|-----------|--------------------------------|
| Patient | Sage Green      | `#84CC16` | Sidebar accent, profile badge  |
| Doctor  | Teal            | `#14B8A6` | Sidebar accent, profile badge  |
| Admin   | Warm Amber      | `#F59E0B` | Sidebar accent, profile badge  |

---

## 3. Typography

Use **[Inter](https://fonts.google.com/specimen/Inter)** as the primary typeface (clean, medical-friendly, excellent readability). Fallback: system sans-serif.

| Element          | Font             | Size      | Weight     | Color            |
|------------------|------------------|-----------|------------|------------------|
| Page Title (H1)  | Inter            | 28px      | 700 (Bold) | `--stone-900`    |
| Section Title (H2)| Inter           | 22px      | 600 (Semi) | `--stone-900`    |
| Subsection (H3)  | Inter            | 18px      | 600        | `--stone-700`    |
| Body Text        | Inter            | 15px      | 400        | `--stone-700`    |
| Small / Caption  | Inter            | 13px      | 400        | `--stone-500`    |
| Button Text      | Inter            | 15px      | 600        | white / `--lime-800` |
| Input Label      | Inter            | 13px      | 500        | `--stone-700`    |
| Badge / Tag      | Inter            | 12px      | 600        | varies           |

---

## 4. Spacing & Layout

| Token     | Value  | Usage                               |
|-----------|--------|-------------------------------------|
| `--sp-1`  | 4px    | Tight internal spacing              |
| `--sp-2`  | 8px    | Small gaps, icon-to-text            |
| `--sp-3`  | 12px   | Input padding, card internal margin |
| `--sp-4`  | 16px   | Default element spacing             |
| `--sp-5`  | 20px   | Card padding                        |
| `--sp-6`  | 24px   | Section gaps                        |
| `--sp-8`  | 32px   | Page top/bottom margin              |
| `--sp-10` | 40px   | Major section separators            |

**Border Radius:**

| Token    | Value | Usage                     |
|----------|-------|---------------------------|
| `--r-sm` | 6px   | Inputs, small buttons     |
| `--r-md` | 10px  | Cards, modals             |
| `--r-lg` | 16px  | Feature cards, avatars    |
| `--r-xl` | 24px  | Pill buttons, tags        |
| `--r-full`| 9999px| Circular avatars, status dots |

---

## 5. Shared Layout Structure

All three interfaces share the same shell:

```
┌──────────────────────────────────────────────┐
│  TOP BAR  (logo · role badge · user menu)    │
├──────────────┬───────────────────────────────┤
│              │                               │
│   SIDEBAR    │       MAIN CONTENT            │
│   (nav)      │       (scrollable)            │
│              │                               │
│              │                               │
│              │                               │
│              │                               │
│              │                               │
├──────────────┴───────────────────────────────┤
│  (optional) BOTTOM STATUS BAR / TOAST AREA   │
└──────────────────────────────────────────────┘
```

- **Top Bar:** Height `64px`. Background `--beige-50`. Logo on left, user avatar + dropdown on right.
- **Sidebar:** Width `260px`, collapsible to `72px` (icon-only). Background `white`. Active link highlighted with role accent color.
- **Main Content:** Background `--beige-50`. Max content width `1200px`, centered. Padding `--sp-8`.
- **Mobile:** Sidebar collapses into a hamburger drawer. Top bar becomes sticky.

---

## 6. Shared Components

### 6.1 Buttons

| Variant     | Background       | Text Color     | Border           | Usage                         |
|-------------|------------------|----------------|------------------|-------------------------------|
| Primary     | `--lime-500`     | `white`        | none             | Main CTAs (Create, Save, Submit) |
| Secondary   | `transparent`    | `--lime-700`   | 1px `--lime-500` | Cancel, secondary actions     |
| Destructive | `--error`        | `white`        | none             | Delete, revoke actions        |
| Ghost       | `transparent`    | `--stone-700`  | none             | Tertiary actions, close       |

**States:** Hover darkens by one shade. Focus shows 3px offset ring in `--lime-400` at 40% opacity. Disabled at 50% opacity, no pointer cursor.

**Sizes:** `sm` (32px height), `md` (40px), `lg` (48px).

### 6.2 Input Fields

- Height: `42px`
- Background: `--stone-100`
- Border: `1px solid --stone-200`, on focus → `--lime-500`
- Border radius: `--r-sm`
- Label above in `--stone-700`, 13px semi-bold
- Error state: border turns `--error`, error message below in `--error` 13px
- Placeholder color: `--beige-400`

### 6.3 Cards

- Background: `white`
- Border: `1px solid --beige-200`
- Border radius: `--r-md`
- Padding: `--sp-5`
- Box shadow: `0 1px 3px rgba(0,0,0,0.06)`
- Hover (if interactive): shadow elevates to `0 4px 12px rgba(0,0,0,0.08)`

### 6.4 Tables

- Header row: background `--beige-100`, text `--stone-700` 13px semi-bold, uppercase
- Body rows: alternating `white` / `--stone-50`
- Row hover: `--beige-50`
- Cell padding: `12px 16px`
- Border between rows: `1px solid --stone-200`

### 6.5 Badges / Tags

| Variant   | Background         | Text             | Usage                         |
|-----------|--------------------|------------------|-------------------------------|
| Active    | `--lime-400` @ 20% | `--lime-800`     | Active status, permissions    |
| Pending   | `--warning` @ 20%  | `#92400E`        | Pending verifications         |
| Completed | `--success` @ 20%  | `#166534`        | Completed consultations       |
| Revoked   | `--error` @ 20%    | `#991B1B`        | Revoked access                |
| Info      | `--info` @ 20%     | `#1E40AF`        | Informational labels          |
| Severity-Mild     | `#FEF3C7`  | `#92400E`        | Mild allergy severity         |
| Severity-Moderate | `#FFEDD5`  | `#9A3412`        | Moderate severity             |
| Severity-Severe   | `#FEE2E2`  | `#991B1B`        | Severe allergy severity       |

### 6.6 Modals / Dialogs

- Overlay: `rgba(0,0,0,0.4)` with backdrop blur `4px`
- Dialog: white, max-width `520px`, border radius `--r-md`, padding `--sp-6`
- Title: H3 styling at top
- Actions at bottom right, primary on right, secondary on left
- Close "X" button in top-right corner (ghost variant)

### 6.7 Toast Notifications

- Slide in from top-right, auto-dismiss after 5 seconds
- Width `360px`, border-radius `--r-md`, shadow prominent
- Left edge colored border (4px) matching severity (success/error/warning/info)
- Includes icon, message, and dismiss "X"

### 6.8 Empty States

- Centered illustration (simple line-art style)
- Heading: "No [items] yet"
- Subtext: one-line description
- Optional CTA button below

### 6.9 Loading States

- Skeleton loaders: animated shimmer rectangles matching the content shape
- Button loading: spinner icon replaces text, button disabled
- Full-page initial load: centered CareLedger logo with pulse animation

---

## 7. Navigation Patterns

### Sidebar Nav Items

Each nav item consists of: **Icon** (20px) + **Label** (15px). Active item has a left border (3px) in the role accent color and the icon/label in accent color. Inactive items are `--stone-500`.

### Breadcrumbs

Shown below the top bar for nested pages. Format: `Dashboard / Consultations / Consultation #12345`. Links in `--info`, current page in `--stone-900`.

---

## 8. Responsive Breakpoints

| Breakpoint | Width      | Behavior                                    |
|------------|------------|---------------------------------------------|
| Desktop    | ≥ 1024px   | Full sidebar + content layout               |
| Tablet     | 768–1023px | Collapsed sidebar (icons only), full content |
| Mobile     | < 768px    | Hidden sidebar (hamburger), stacked layout  |

---

## 9. Animations & Transitions

| Element            | Transition                                                  |
|--------------------|-------------------------------------------------------------|
| Buttons            | `background-color 150ms ease, transform 100ms ease`         |
| Cards (hover)      | `box-shadow 200ms ease, transform 200ms ease`               |
| Sidebar collapse   | `width 250ms ease-in-out`                                   |
| Modal appear       | Overlay fade `200ms ease`, dialog scale `200ms ease` (0.95→1) |
| Toast appear       | Slide from right `300ms ease-out`                           |
| Page transitions   | Content fade `150ms ease`                                   |
| Skeleton shimmer   | Linear gradient sweep `1.5s ease-in-out infinite`           |

---

## 10. Iconography

Use **[Lucide Icons](https://lucide.dev/)** — clean, consistent, open-source. 20px for inline, 24px for navigation.

Key icons per feature:

| Feature          | Icon Name          |
|------------------|--------------------|
| Dashboard        | `layout-dashboard` |
| Profile          | `user`             |
| Consultations    | `stethoscope`      |
| Medications      | `pill`             |
| Allergies        | `alert-triangle`   |
| Chronic Conditions| `heart-pulse`     |
| Emergency Info   | `phone-call`       |
| Clinics          | `building-2`       |
| Prescriptions    | `clipboard-list`   |
| Access Control   | `shield-check`     |
| OCR Scan         | `scan`             |
| Settings         | `settings`         |
| Logout           | `log-out`          |
| Verify           | `check-circle`     |
| Users            | `users`            |
| Delete           | `trash-2`          |
| Edit             | `pencil`           |
| Add              | `plus`             |

---

## 11. Authentication Flow (Shared)

This flow is identical for all user roles.

### Login Page

```
┌──────────────────────────────────────┐
│                                      │
│         🏥 CareLedger                │
│         "Your health, your ledger"   │
│                                      │
│   ┌──────────────────────────────┐   │
│   │  Role Selector Tabs          │   │
│   │  [ Patient | Doctor | Admin ]│   │
│   └──────────────────────────────┘   │
│                                      │
│   ┌──────────────────────────────┐   │
│   │  Email or Phone              │   │
│   └──────────────────────────────┘   │
│   ┌──────────────────────────────┐   │
│   │  Password                    │   │
│   └──────────────────────────────┘   │
│                                      │
│   [ ████████ Login ████████ ]        │
│                                      │
│   Don't have an account? Sign Up     │
│                                      │
└──────────────────────────────────────┘
```

- **Background:** Subtle gradient from `--beige-50` to `--beige-100`
- **Card:** Centered, white, max-width `420px`, shadow, `--r-md`
- **Role selector:** Segmented control style tabs. Selected tab uses the role's accent color.
- **Login button:** Primary `--lime-500`, full width

**API Integration:**
- `POST /api/users/login` with `{ email?, phone?, role, plain_password }`
- Store JWT token in `localStorage` or secure cookie
- Decode token to get `userId` and `role` for routing

### Signup Page

Same layout as login. Additional fields:

- Email input
- Phone input
- Password input
- Confirm Password input (client-side only)
- Role selector: **Patient** | **Doctor** (admin cannot self-register)

**API Integration:** `POST /api/users/signup`

### Post-Login Routing

| Role    | Redirect To                  |
|---------|------------------------------|
| Patient | `/patient/dashboard`         |
| Doctor  | `/doctor/dashboard`          |
| Admin   | `/admin/dashboard`           |

---

## 12. Shared Utilities

### Token Handling

- Store JWT in `localStorage` (key: `careledger_token`)
- Attach to every API request via `Authorization: Bearer <token>` header
- On `401` response → redirect to login page
- On `403` response → show "Access Denied" toast

### API Error Display

Map all API error responses to user-friendly toasts:

| Error Code        | Toast Variant | User Message                           |
|-------------------|---------------|----------------------------------------|
| `BAD_REQUEST`     | Warning       | "Please check your input and try again"|
| `VALIDATION_ERROR`| Warning       | Display the error `message` directly   |
| `UNAUTHORIZED`    | Error         | "Session expired. Please log in again" |
| `FORBIDDEN`       | Error         | "You don't have permission for this"   |
| `NOT_FOUND`       | Warning       | "The requested item was not found"     |
| `CONFLICT`        | Warning       | Display the error `message` directly   |
| `INTERNAL_ERROR`  | Error         | "Something went wrong. Please retry"   |


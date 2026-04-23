# 🏥 CareLedger

> **Modern Healthcare Management Platform**  
> Bridging the gap between patients, doctors, and healthcare data with seamless digital solutions.

<div align="center">

![Status](https://img.shields.io/badge/status-active-success)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Node](https://img.shields.io/badge/node-%3E%3D16.0.0-brightgreen)
![React](https://img.shields.io/badge/react-%5E18.3.1-61dafb)
![PostgreSQL](https://img.shields.io/badge/postgresql-%3E%3D14-336791)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Database Schema](#-database-schema)
- [OCR Processing Flow](#-ocr-processing-flow)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**CareLedger** is a comprehensive healthcare management system that digitizes and streamlines medical record management, prescription handling, and patient-doctor interactions. Built with modern web technologies, it provides a secure, scalable, and user-friendly platform for managing electronic health records (EHR).

### Key Capabilities

- 👥 **Multi-Role Platform** - Dedicated interfaces for patients, doctors, and administrators
- 📋 **Electronic Prescriptions** - Digital prescription management with medication tracking
- 🔍 **OCR Processing** - Intelligent document scanning for legacy medical records
- 🏥 **Clinic Management** - Doctor clinic profiles and appointment coordination
- 🚨 **Emergency Information** - Critical patient data accessible in emergencies
- 📊 **Chronic Condition Tracking** - Long-term health monitoring and management
- 🛡️ **Role-Based Access Control** - Secure, permission-based data access

---

## ✨ Features

### For Patients

- 📱 **Personal Health Dashboard** - View medical history, prescriptions, and test results
- 💊 **Active Medications** - Track current prescriptions and dosage schedules
- 🚑 **Emergency Contacts** - Store and manage emergency contact information
- 📄 **Legacy Documents** - Upload and manage historical medical records
- 🔐 **Access Control** - Grant/revoke doctor access to medical records
- 📅 **Consultation History** - Complete record of doctor visits and diagnoses

### For Doctors

- 👨‍⚕️ **Practice Management** - Manage multiple clinic locations
- 📝 **Digital Prescriptions** - Create and issue electronic prescriptions
- 🏥 **Patient Records Access** - View authorized patient medical histories
- 🚨 **Emergency Access** - Critical patient information in urgent situations
- ✅ **Verification System** - Verified doctor badge for trust and authenticity

### For Administrators

- 👥 **User Management** - Oversee patient and doctor accounts
- 🔍 **Verification** - Doctor credential verification and approval
- 📊 **System Analytics** - Platform usage and performance metrics
- 🛡️ **Compliance** - Ensure HIPAA and healthcare regulation adherence

---

## 🏗️ Architecture

CareLedger follows a modern **client-server architecture** with RESTful APIs and a relational database backend.

```mermaid
flowchart TB
    subgraph Client["🖥️ Frontend Layer"]
        P[Patient Web App]
        D[Doctor Web App]
        A[Admin Dashboard]
    end
    
    subgraph API["⚡ API Gateway"]
        LB[Load Balancer]
        AUTH[Auth Middleware]
        ROUTER[API Router]
    end
    
    subgraph Services["🔧 Business Logic"]
        USR[User Service]
        PAT[Patient Service]
        DOC[Doctor Service]
        OCR[OCR Service]
        PDF[PDF Service]
        EMAIL[Email Service]
    end
    
    subgraph Data["💾 Data Layer"]
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
        STORAGE[File Storage]
    end
    
    P --> LB
    D --> LB
    A --> LB
    LB --> AUTH
    AUTH --> ROUTER
    ROUTER --> USR
    ROUTER --> PAT
    ROUTER --> DOC
    ROUTER --> OCR
    ROUTER --> PDF
    ROUTER --> EMAIL
    USR --> DB
    PAT --> DB
    DOC --> DB
    OCR --> STORAGE
    PDF --> STORAGE
    EMAIL --> CACHE

    classDef client fill:#e0f2fe,stroke:#0369a1,stroke-width:2px
    classDef api fill:#fef3c7,stroke:#b45309,stroke-width:2px
    classDef service fill:#dcfce7,stroke:#15803d,stroke-width:2px
    classDef data fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px
    
    class P,D,A client
    class LB,AUTH,ROUTER api
    class USR,PAT,DOC,OCR,PDF,EMAIL service
    class DB,CACHE,STORAGE data
```

---

## 🗄️ Database Schema

Our database is designed with data integrity, normalization, and query performance in mind.

```mermaid
flowchart LR
    USERS["fa:fa-users USERS<br/>--------------------<br/><u>id</u> (PK)<br/>email (UK)<br/>phone (UK)<br/>password_hash<br/>role<br/>created_at"]
    PATIENTS["fa:fa-user-injured PATIENTS<br/>--------------------<br/><u>id</u> (PK)<br/>user_id (FK)<br/>health_id (UK)<br/>full_name<br/>date_of_birth<br/>gender<br/>blood_group"]
    DOCTORS["fa:fa-user-md DOCTORS<br/>--------------------<br/><u>id</u> (PK)<br/>user_id (FK)<br/>full_name<br/>license_number (UK)<br/>specialization<br/>is_verified<br/>updated_at<br/>created_at"]
    CLINICS["fa:fa-clinic-medical CLINICS<br/>--------------------<br/><u>id</u> (PK)<br/>doctor_id (FK)<br/>clinic_name<br/>address<br/>logo_url<br/>email<br/>phone<br/>created_at<br/>updated_at"]
    CONSULTATIONS["fa:fa-stethoscope CONSULTATIONS<br/>--------------------<br/><u>id</u> (PK)<br/>patient_id (FK)<br/>doctor_id (FK)<br/>consultation_date<br/>status<br/>updated_at"]
    PRESCRIPTIONS["fa:fa-file-prescription PRESCRIPTIONS<br/>--------------------<br/><u>id</u> (PK)<br/>consultation_id (FK, UK)<br/>patient_id (FK)<br/>doctor_id (FK)<br/>issued_at<br/>created_at<br/>updated_at<br/>doctor_notes"]
    PRESCRIPTION_ITEMS["fa:fa-capsules PRESCRIPTION_ITEMS<br/>--------------------<br/><u>id</u> (PK)<br/>prescription_id (FK)<br/>drug_name<br/>dosage<br/>frequency<br/>duration_days"]
    ACTIVE_MEDICATION["fa:fa-pills ACTIVE_MEDICATION<br/>--------------------<br/><u>id</u> (PK)<br/>name<br/>dosage<br/>prescibed_for<br/>prescibed_at<br/>prescribed_by (FK)<br/>patient_id (FK)<br/>doctor_name"]
    ALLERGIES["fa:fa-exclamation-triangle ALLERGIES<br/>--------------------<br/><u>id</u> (PK)<br/>patient_id (FK)<br/>allergen<br/>severity"]
    CHRONIC_CONDITIONS["fa:fa-heartbeat CHRONIC_CONDITIONS<br/>--------------------<br/><u>id</u> (PK)<br/>patient_id (FK)<br/>condition_name<br/>status<br/>diagnosed_date"]
    EMERGENCY_INFO["fa:fa-ambulance EMERGENCY_INFO<br/>--------------------<br/><u>id</u> (PK)<br/>patient_id (FK)<br/>contact_name<br/>contact_phone<br/>contact_relationship<br/>contact_email"]
    ACCESS_PERMISSIONS["fa:fa-key ACCESS_PERMISSIONS<br/>--------------------<br/><u>id</u> (PK)<br/>patient_id (FK)<br/>doctor_id (FK)<br/>status<br/>expires_at<br/>created_at<br/>updated_at"]
    R_HAS_PATIENT{"fa:fa-link HAS"}
    R_HAS_DOCTOR{"fa:fa-link HAS"}
    R_RUNS_CLINIC{"fa:fa-hospital RUNS"}
    R_BOOKS{"fa:fa-calendar-check BOOKS"}
    R_CONDUCTS{"fa:fa-user-md CONDUCTS"}
    R_GENERATES_RX{"fa:fa-file-medical GENERATES"}
    R_HAS_ITEMS{"fa:fa-list HAS_ITEMS"}
    R_TRACKS_MEDS{"fa:fa-notes-medical TRACKS"}
    R_HAS_ALLERGIES{"fa:fa-exclamation-circle HAS"}
    R_HAS_CONDITIONS{"fa:fa-procedures HAS"}
    R_HAS_EMERGENCY{"fa:fa-first-aid HAS"}
    R_GRANTS_ACCESS{"fa:fa-unlock-alt GRANTS"}
    USERS -- "1" --- R_HAS_PATIENT
    R_HAS_PATIENT -- "0..1" --- PATIENTS
    USERS -- "1" --- R_HAS_DOCTOR
    R_HAS_DOCTOR -- "0..1" --- DOCTORS
    DOCTORS -- "1" --- R_RUNS_CLINIC
    R_RUNS_CLINIC -- "0..N" --- CLINICS
    PATIENTS -- "1" --- R_BOOKS
    R_BOOKS -- "0..N" --- CONSULTATIONS
    DOCTORS -- "1" --- R_CONDUCTS
    R_CONDUCTS -- "0..N" --- CONSULTATIONS
    CONSULTATIONS -- "1" --- R_GENERATES_RX
    R_GENERATES_RX -- "0..1" --- PRESCRIPTIONS
    PRESCRIPTIONS -- "1" --- R_HAS_ITEMS
    R_HAS_ITEMS -- "1..N" --- PRESCRIPTION_ITEMS
    PATIENTS -- "1" --- R_TRACKS_MEDS
    R_TRACKS_MEDS -- "0..N" --- ACTIVE_MEDICATION
    DOCTORS -- "1" --- R_TRACKS_MEDS
    PATIENTS -- "1" --- R_HAS_ALLERGIES
    R_HAS_ALLERGIES -- "0..N" --- ALLERGIES
    PATIENTS -- "1" --- R_HAS_CONDITIONS
    R_HAS_CONDITIONS -- "0..N" --- CHRONIC_CONDITIONS
    PATIENTS -- "1" --- R_HAS_EMERGENCY
    R_HAS_EMERGENCY -- "0..N" --- EMERGENCY_INFO
    PATIENTS -- "1" --- R_GRANTS_ACCESS
    R_GRANTS_ACCESS -- "0..N" --- ACCESS_PERMISSIONS
    DOCTORS -- "1" --- R_GRANTS_ACCESS
    PATIENTS -- "1" --- PRESCRIPTIONS
    DOCTORS -- "1" --- PRESCRIPTIONS

    classDef entity fill:#eaf3ff,stroke:#1d4ed8,stroke-width:2.2px,color:#0b2a6f,font-size:16px
    classDef relation fill:#dbeafe,stroke:#1e40af,stroke-width:2.6px,color:#0b2a6f,font-size:17px,font-weight:bold
    class USERS,PATIENTS,DOCTORS,CLINICS,CONSULTATIONS,PRESCRIPTIONS,PRESCRIPTION_ITEMS,ACTIVE_MEDICATION,ALLERGIES,CHRONIC_CONDITIONS,EMERGENCY_INFO,ACCESS_PERMISSIONS entity
    class R_HAS_PATIENT,R_HAS_DOCTOR,R_RUNS_CLINIC,R_BOOKS,R_CONDUCTS,R_GENERATES_RX,R_HAS_ITEMS,R_TRACKS_MEDS,R_HAS_ALLERGIES,R_HAS_CONDITIONS,R_HAS_EMERGENCY,R_GRANTS_ACCESS relation
```

### Core Entities

| Entity | Description | Key Relationships |
|--------|-------------|-------------------|
| **Users** | Authentication & authorization base | 1:1 with Patients/Doctors |
| **Patients** | Patient health profiles | Many consultations, prescriptions |
| **Doctors** | Medical practitioner profiles | Many clinics, consultations |
| **Clinics** | Doctor practice locations | Owned by doctors |
| **Consultations** | Patient-doctor encounters | Generates prescriptions |
| **Prescriptions** | Medical prescriptions | Contains prescription items |
| **Active Medications** | Current medication tracking | Linked to patients & doctors |
| **Allergies** | Patient allergy records | Patient-specific |
| **Chronic Conditions** | Long-term health conditions | Patient-specific |
| **Emergency Info** | Critical emergency contacts | Patient-specific |
| **Access Permissions** | Doctor access grants | Patient-doctor relationships |

---

## 📸 OCR Processing Flow

Our intelligent OCR system processes medical documents and extracts prescription data automatically.

```mermaid
flowchart LR
    CLIENT[Client]
    SCAN[POST /api/ocr/scan]
    LEGACY[POST /api/ocr/legacy-upload]
    HEALTH[GET /api/ocr/health]

    AUTH[Auth patient only]
    UPLOAD[Upload JPG/PNG/PDF]
    CTRL[OCR Controller]
    CHECK{Legacy PDF single page?}
    PARSE[OCR + Parse meds]
    VALID{Valid medication data?}
    SAVE[Save prescription]
    DB[(PostgreSQL)]
    OK[200 OK]
    ERR1[400 VALIDATION_ERROR]
    ERR2[400 DOCUMENT_READ_FAILED]
    CLEAN[Cleanup temp file]
    HSTAT[Health 200/202]

    CLIENT --> SCAN --> UPLOAD --> CTRL --> CHECK
    CLIENT --> LEGACY --> AUTH --> UPLOAD
    CHECK -- Yes --> PARSE
    CHECK -- No --> ERR1 --> CLEAN
    PARSE --> VALID
    VALID -- Yes --> SAVE --> DB --> OK --> CLEAN
    VALID -- No --> ERR2 --> CLEAN

    CLIENT --> HEALTH --> HSTAT

    classDef api fill:#eaf3ff,stroke:#1d4ed8,stroke-width:2px,color:#0b2a6f
    classDef step fill:#ecfeff,stroke:#0e7490,stroke-width:2px,color:#164e63
    classDef decision fill:#fff7ed,stroke:#c2410c,stroke-width:2px,color:#7c2d12
    classDef error fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d
    classDef db fill:#ecfdf5,stroke:#16a34a,stroke-width:2px,color:#14532d
    classDef ok fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d

    class CLIENT,SCAN,LEGACY,HEALTH,AUTH,UPLOAD,CTRL,HSTAT api
    class PARSE,SAVE,CLEAN step
    class CHECK,VALID decision
    class ERR1,ERR2 error
    class DB db
    class OK ok
```

### OCR Capabilities

- 📄 **Multi-Format Support** - JPG, PNG, and PDF documents
- 🧠 **Intelligent Parsing** - Automatic medication data extraction
- ✅ **Validation** - Data integrity checks before storage
- 🗑️ **Auto-Cleanup** - Temporary file management
- 📊 **Health Monitoring** - System status endpoints

---

## 🛠️ Tech Stack

### Frontend

<div align="center">

| Technology | Version | Purpose |
|------------|---------|---------|
| ![React](https://img.shields.io/badge/React-18.3.1-61dafb?logo=react) | 18.3.1 | UI Framework |
| ![Vite](https://img.shields.io/badge/Vite-5.4.19-646cff?logo=vite) | 5.4.19 | Build Tool |
| ![React Router](https://img.shields.io/badge/React_Router-6.30.0-ca424b?logo=react-router) | 6.30.0 | Routing |
| ![TanStack Query](https://img.shields.io/badge/TanStack_Query-5.97.0-ff4154?logo=react-query) | 5.97.0 | Data Fetching |
| ![Axios](https://img.shields.io/badge/Axios-1.8.4-5a29e4?logo=axios) | 1.8.4 | HTTP Client |
| ![Supabase](https://img.shields.io/badge/Supabase-2.103.3-3ecf8e?logo=supabase) | 2.103.3 | Backend Service |
| ![GSAP](https://img.shields.io/badge/GSAP-3.14.2-88ce02?logo=gsap) | 3.14.2 | Animations |
| ![Lenis](https://img.shields.io/badge/Lenis-1.3.21-000000) | 1.3.21 | Smooth Scrolling |
| ![Recharts](https://img.shields.io/badge/Recharts-3.8.1-f56e0f?logo=recharts) | 3.8.1 | Data Visualization |
| ![Lucide](https://img.shields.io/badge/Lucide-0.507.0-000000?logo=lucide) | 0.507.0 | Icons |

</div>

### Backend

<div align="center">

| Technology | Version | Purpose |
|------------|---------|---------|
| ![Node.js](https://img.shields.io/badge/Node.js-%3E%3D16-339933?logo=node.js) | 16+ | Runtime |
| ![Express](https://img.shields.io/badge/Express-4.19.2-000000?logo=express) | 4.19.2 | Web Framework |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-%3E%3D14-336791?logo=postgresql) | 14+ | Database |
| ![JWT](https://img.shields.io/badge/JWT-9.0.3-000000?logo=json-web-tokens) | 9.0.3 | Authentication |
| ![Bcrypt](https://img.shields.io/badge/Bcrypt-6.0.0-000000) | 6.0.0 | Password Hashing |
| ![Multer](https://img.shields.io/badge/Multer-2.1.1-000000) | 2.1.1 | File Uploads |
| ![Nodemailer](https://img.shields.io/badge/Nodemailer-6.10.1-000000?logo=nodemailer) | 6.10.1 | Email Service |
| ![PDF Parse](https://img.shields.io/badge/PDF_Parse-2.4.5-000000) | 2.4.5 | PDF Processing |

</div>

### Development Tools

- **Nodemon** - Development auto-restart
- **ESLint** - Code linting
- **Postman** - API testing
- **Newman** - Automated API testing

---

## 🚀 Installation

### Prerequisites

- Node.js >= 16.0.0
- PostgreSQL >= 14
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Create .env file with required variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev

# Start production server
npm start
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

#### Backend (.env)

```env
# Server
PORT=3000
NODE_ENV=development

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Authentication
JWT_SECRET=your-super-secret-jwt-key

# OCR Service
ENABLE_OCR=true

# Email Service
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-password
```

#### Frontend (.env)

```env
# API Configuration
VITE_API_URL=http://localhost:3000/api

# Supabase Configuration
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:3000/api
```

### Authentication

Protected routes require a JWT Bearer token:

```http
Authorization: Bearer <token>
```

### Endpoints Overview

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/users/signup` | POST | 🔓 | Register new user |
| `/api/users/login` | POST | 🔓 | Authenticate user |
| `/api/patients/*` | Various | 🔐 | Patient operations |
| `/api/doctors/*` | Various | 🔐👨‍⚕️ | Doctor operations |
| `/api/consultations/*` | Various | 🔐 | Consultation management |
| `/api/medications/*` | Various | 🔐 | Medication tracking |
| `/api/clinics/*` | Various | 🔐👨‍⚕️ | Clinic management |
| `/api/ocr/*` | Various | 🔐 | OCR processing |
| `/api/admin/*` | Various | 🔐👑 | Admin operations |

### Response Format

#### Success Response

```json
{
  "success": true,
  "data": { /* resource payload */ },
  "message": "Operation successful."
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message."
  }
}
```

For complete API documentation, see [API Documentation](./backend/api-documentation.md).

---

## 📁 Project Structure

```
chr-eps-backend/
├── backend/
│   ├── server.js                 # Application entry point
│   ├── package.json              # Backend dependencies
│   ├── api-documentation.md      # Complete API reference
│   ├── src/
│   │   ├── app.js                # Express app configuration
│   │   ├── config/
│   │   │   └── db.js             # Database connection
│   │   ├── controllers/          # Request handlers
│   │   │   ├── userController.js
│   │   │   ├── patientController.js
│   │   │   ├── doctorController.js
│   │   │   ├── ocrController.js
│   │   │   └── ...
│   │   ├── middlewares/          # Express middlewares
│   │   │   ├── authMiddleware.js
│   │   │   ├── roleMiddleware.js
│   │   │   └── errorHandler.js
│   │   ├── routes/               # API route definitions
│   │   │   ├── api.js
│   │   │   ├── userRoutes.js
│   │   │   ├── patientRoutes.js
│   │   │   └── ...
│   │   ├── services/             # Business logic
│   │   │   ├── emailService.js
│   │   │   ├── pdfService.js
│   │   │   └── ocrService.js
│   │   └── utils/                # Helper functions
│   │       ├── validators.js
│   │       ├── responseFormatter.js
│   │       └── ocrManager.js
│   ├── OCR_processor/            # OCR processing module
│   │   ├── ocr_init.py
│   │   ├── ocr_service.py
│   │   └── ...
│   └── Database/
│       └── migration.sql         # Database schema
│
├── frontend/
│   ├── package.json              # Frontend dependencies
│   ├── vite.config.js            # Vite configuration
│   ├── index.html                # HTML entry point
│   └── src/
│       ├── App.jsx               # Main app component
│       ├── main.jsx              # React entry point
│       ├── api/                  # API client modules
│       ├── components/           # Reusable UI components
│       ├── context/              # React context providers
│       ├── hooks/                # Custom React hooks
│       ├── pages/                # Page components
│       ├── styles/               # CSS stylesheets
│       └── utils/                # Utility functions
│
├── testing/
│   └── postman/                  # API testing collections
│       ├── CareLedger-API-Testing.postman_collection.json
│       └── CareLedger-Local.postman_environment.json
│
├── er.mermaid                    # Entity Relationship Diagram
├── ocr.mermaid                   # OCR Flow Diagram
└── README.md                     # This file
```

---

## 🔒 Security

### Authentication & Authorization

- **JWT-based Authentication** - Secure token-based auth with 24-hour expiry
- **Role-Based Access Control (RBAC)** - Patient, Doctor, and Admin roles
- **Password Hashing** - Bcrypt with salt rounds for secure password storage
- **Middleware Protection** - Route-level authentication and authorization

### Data Protection

- **CORS Configuration** - Controlled cross-origin resource sharing
- **Input Validation** - Request body validation and sanitization
- **SQL Injection Prevention** - Parameterized queries via pg driver
- **File Upload Security** - Multer with file type and size restrictions

### Compliance

- **HIPAA Considerations** - Healthcare data privacy best practices
- **Audit Logging** - Track access and modifications to sensitive data
- **Access Permissions** - Patient-controlled doctor access grants

---

## 🤝 Contributing

We welcome contributions to CareLedger! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Workflow

```bash
# Clone your fork
git clone https://github.com/your-username/chr-eps-backend.git

# Install dependencies
cd backend && npm install
cd ../frontend && npm install

# Start development servers
# Terminal 1 - Backend
cd backend && npm run dev

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Code Standards

- Follow ESLint configuration
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support, please open an issue in the repository or contact the development team.

---

<div align="center">

**Made with ❤️ for better healthcare**

![Stars](https://img.shields.io/github/stars/your-username/chr-eps-backend?style=social)
![Forks](https://img.shields.io/github/forks/your-username/chr-eps-backend?style=social)
![Issues](https://img.shields.io/github/issues/your-username/chr-eps-backend)
![Pull Requests](https://img.shields.io/github/issues-pr/your-username/chr-eps-backend)

</div>

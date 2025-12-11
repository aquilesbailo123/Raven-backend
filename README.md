<div align="center">
  <h1>🦅 Raven CRM</h1>
</div>

# Raven CRM

A comprehensive Customer Relationship Management system designed for startup incubators and accelerators to manage their portfolio, track progress, and facilitate growth.

## Overview

Raven CRM is a dual-view platform that serves both startups and incubators, providing a complete ecosystem for managing the incubation pipeline, tracking technology and commercial readiness levels, financial analysis, investor relations, challenges, and mentoring programs.

## Two Main Views

### 🚀 Startup View
Designed for individual startups to manage their own progress, track milestones, and engage with incubator resources.

### 🏢 Incubator View
Comprehensive dashboard for incubators to manage their entire portfolio, track multiple startups, and oversee the incubation process at scale.

## Key Modules

### 🔐 Dual Authentication
- **Startup Login**: Rocket icon (blue theme) with professional animations and gradients
  - Create account
  - Password recovery
  - Modern UI with smooth transitions
- **Incubator Login**: Building icon (purple theme) with professional animations and gradients
  - Create account
  - Password recovery
  - Branded experience

### 📊 Incubation Pipeline
- **Startup View**: 
  - Individual progress dashboard
  - Kanban board with 4 stages: Pre-incubación, Incubación, Aceleración, Exit
  - Card view (grid/list toggle)
  - Drag & drop functionality
  - Key information display: logo, founders, revenue, progress indicators
- **Incubator View**:
  - Portfolio-wide pipeline management
  - Multi-startup tracking
  - Consolidated progress views

### 📈 TRL/CRL (Technology Readiness Level / Commercial Readiness Level)
- **Startup View**:
  - Personal logbook/bitácora
  - 9 levels for both TRL and CRL
  - Visual state indicators
  - Evidence uploads and gallery
  - Tab navigation between TRL and CRL
  - Progress indicators
- **Incubator View**:
  - View logbooks for all managed startups
  - Access to all evidence and uploads
  - Tab navigation and progress tracking across portfolio
  - Consolidated reporting

### 💰 Finanzas (Finance)
- **Startup View**:
  - Company-specific KPIs and charts
  - Viability indicators: profit, EBITDA, NPV, IRR, ROE
  - Financial projections
  - Sensitivity analysis
  - Cash flow tables
  - Export to Excel/CSV
- **Incubator View**:
  - Portfolio-wide KPIs
  - Consolidated view and export by startup
  - Portfolio-level exports
  - Aggregated statistical projections

### 💼 Inversores (Investors)
- **Startup View**:
  - List and manage investors
  - Visualize investment status/tickets
  - Track funding rounds (pre-seed, seed, Series A, donations)
  - KuskaPay integration
  - Crowdfunding CTA
- **Incubator View**:
  - View and manage investors accepted by startups
  - Track rounds and global participation
  - KuskaPay integration at portfolio level
  - Consolidated investor management

### 🎯 Desafíos (Challenges - Open Window)
- **Startup View**:
  - Browse and apply to business challenges
  - Track application status
  - Chat with matched companies
- **Incubator View**:
  - Manage and review all received challenges
  - Administer participating startups
  - Match startups with challenges

### 👥 Mentoring
- **Startup View**:
  - Directory of registered mentors
  - Filter and schedule sessions
  - Rating and feedback system
  - Personal notes and history
- **Incubator View**:
  - Extended directory for entire network
  - Track progress and sessions of mentored startups
  - Mentor notes and feedback
  - Network-wide mentoring analytics

### 🎨 Transversal Elements
- **UI/UX Components**:
  - Fixed sidebar with role-based navigation
  - Header with search, notifications, and avatar
  - Color palette: Blue theme for startups, Purple theme for incubators
  - Stage-based status indicators
  - Modern typography and components
  - Fully responsive design
  - Loading states and empty states
  - Accessible design patterns

## Project Structure

```
raven-crm/
├── backend/               # Main Django configuration
│   ├── settings/          # Modular settings files
│   └── ...
├── build_scripts/         # Deployment scripts
├── core/                  # Core functionality and shared components
├── users/                 # User management and dual authentication
├── startups/              # Startup management module
├── incubators/            # Incubator management module
├── pipeline/              # Incubation pipeline module
├── trl_crl/              # TRL/CRL tracking module
├── finanzas/             # Finance module
├── inversores/           # Investors module
├── desafios/             # Challenges module
├── mentoring/            # Mentoring module
├── utils/                # Utility functions and helpers
└── static/               # Static files
```

## Prototype

For a detailed review of the proposed prototype, visit:
[Figma Prototype - Raven CRM](https://www.figma.com/make/MlvuxcvTJIhXJaYlCXEdb2/Raven-CRM?t=Q7cDcHqcxnurKZU5&fullscreen=1)

## Getting Started

1. Clone the repository
2. Copy `.env.template` to `.env` and set your environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Run the server: `python manage.py runserver`

## Deployment

Use the provided build script for deployment:

```bash
./build_scripts/render.sh
```

## Management Scripts

### Delete Non-Admin Users
To delete all users except superusers and staff (useful for cleaning up test data):

```bash
python delete_non_admin_users.py
```

## Extending the Project

This CRM is designed to be extended. When adding new functionality:

1. Create a new Django app if needed: `python manage.py startapp app_name`
2. Follow the established patterns for models, views, and serializers
3. Update the settings as needed
4. Register the app in `INSTALLED_APPS` in settings

## License

This project is freely available for use without restrictions. Anyone who clones this repository is welcome to use, modify, and distribute it as they see fit. No attribution required.

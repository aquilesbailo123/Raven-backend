  # MODEL.md

  ## Overview
  This document provides a comprehensive overview of the **database schema** and **API endpoints** for the **Raven** Django backend. It includes:
  - All models (tables) with field definitions, data types, nullability, primary/foreign keys.
  - Relationships (One‑to‑One, One‑to‑Many, Many‑to‑One, Many‑to‑Many).
  - REST API routes (generated via `router.register` and explicit `path` definitions).
  - Request/Response payloads for each endpoint.
  - Example **Axios + TypeScript** calls.

  > **Note:** The project follows the file‑upload pattern where files are stored in Google Cloud Storage; only URL fields are persisted.

  ---

  ## 1. Database Models
  ### 1.1 Core Models (`core/models.py`)
  | Table | Column | Type | Null | Primary Key | Foreign Key | Description |
  |-------|--------|------|------|-------------|-------------|-------------|
  | `BaseModel` (abstract) | `id` | `AutoField` | No | Yes | – | Base primary key (auto‑generated). |
  | | `created` | `DateTimeField` (auto_now_add) | No | – | – | Timestamp of creation. |
  | | `updated` | `DateTimeField` (auto_now) | No | – | – | Timestamp of last update. |
  | `UserMixinModel` (abstract) | `user_id` | `ForeignKey` → `auth_user` | Yes | – | Yes | Links to Django's built‑in user model (nullable for optional association). |

  ### 1.2 Users App (`users/models.py`)

  #### Modelo: `Profile`
  | Column | Type | Null | PK | FK | Relationship |
  |--------|------|------|----|----|--------------|
  | `id` | `AutoField` | No | Yes | – | – |
  | `user_id` | `OneToOneField → auth_user` | No | – | Yes | One‑to‑One with `auth_user` |
  | `user_type` | `CharField(20)` | No | – | – | Choices: `startup`, `incubator` |
  | `actions_freezed_till` | `DateTimeField` | Yes | – | – | Nullable timestamp for action freeze |

  #### Modelo: `Startup`
  | Column | Type | Null | PK | FK | Relationship |
  |--------|------|------|----|----|--------------|
  | `id` | `AutoField` | No | Yes | – | – |
  | `profile_id` | `OneToOneField → Profile` | No | – | Yes | One‑to‑One (each profile has one startup) |
  | `company_name` | `CharField(255)` | Yes | – | – | – |
  | `industry` | `CharField(50)` | Yes | – | – | – |
  | `logo_url` | `URLField` | Yes | – | – | – |
  | `TRL_level` | `IntegerField` | No | – | – | Default: 1, Choices: 1-9 |
  | `CRL_level` | `IntegerField` | No | – | – | Default: 1, Choices: 1-9 |
| `incubators` | `ManyToManyField → Incubator` | Yes | – | – | Many‑to‑Many (Startup can be associated with multiple Incubators) |

#### Modelo: `Incubator`
| Column | Type | Null | PK | FK | Relationship |
|--------|------|------|----|----|--------------|
| `id` | `AutoField` | No | Yes | – | – |
| `profile_id` | `OneToOneField → Profile` | No | – | Yes | One‑to‑One (each profile has one incubator) |
| `name` | `CharField(255)` | No | – | – | – |
| `description` | `TextField` | Yes | – | – | – |
| `logo_url` | `URLField` | Yes | – | – | – |
| `profile_complete` | `BooleanField` (default=False) | No | – | – | – |
| `investments` | `Reverse ForeignKey → Investor` | Yes | – | – | One-to-Many (Incubator has many investments) |

#### Modelo: `IncubatorMember`
| Column | Type | Null | PK | FK | Relationship |
|--------|------|------|----|----|--------------|
| `id` | `AutoField` | No | Yes | – | – |
| `incubator_id` | `ForeignKey → Incubator` | No | – | Yes | Many‑to‑One |
| `full_name` | `CharField(255)` | No | – | – | – |
| `email` | `EmailField` | No | – | – | – |
| `phone` | `CharField(50)` | Yes | – | – | – |
| `role` | `CharField(20)` | No | – | – | Choices: `INVESTOR`, `MENTOR`, `BOTH` |

#### Modelo: `Challenge`
| Column | Type | Null | PK | FK | Relationship |
|--------|------|------|----|----|--------------|
| `id` | `AutoField` | No | Yes | – | – |
| `incubator_id` | `ForeignKey → Incubator` | No | – | Yes | Many‑to‑One |
| `title` | `CharField(255)` | No | – | – | – |
| `subtitle` | `CharField(255)` | Yes | – | – | – |
| `description` | `TextField` | No | – | – | – |
| `budget` | `DecimalField` | Yes | – | – | – |
| `deadline` | `DateField` | Yes | – | – | – |
| `required_technologies` | `TextField` | No | – | – | – |
| `status` | `CharField(20)` | No | – | – | Choices: `OPEN`, `CONCLUDED` |

#### Modelo: `ChallengeApplication`
| Column | Type | Null | PK | FK | Relationship |
|--------|------|------|----|----|--------------|
| `id` | `AutoField` | No | Yes | – | – |
| `challenge_id` | `ForeignKey → Challenge` | No | – | Yes | Many‑to‑One |
| `startup_id` | `ForeignKey → Startup` | No | – | Yes | Many‑to‑One |
| `text_solution` | `TextField` | No | – | – | – |

#### Modelo: `InvestorPipeline`
| Column | Type | Null | PK | FK | Relationship |
|--------|------|------|----|----|--------------|
| `id` | `AutoField` | No | Yes | – | – |
| `challenge_id` | `ForeignKey → Challenge` | No | – | Yes | Many‑to‑One |
| `startup_id` | `ForeignKey → Startup` | No | – | Yes | Many‑to‑One |
| `round_id` | `ForeignKey → InvestmentRound` | Yes | – | Yes | Many‑to‑One (Optional) |
| `investor_name` | `CharField(255)` | No | – | – | – |

  #### Modelo: `ReadinessLevel`
  | Column | Type | Null | PK | FK | Relationship |
  |--------|------|------|----|----|--------------|
  | `id` | `AutoField` | No | Yes | – | – |
  | `startup_id` | `ForeignKey → Startup` | No | – | Yes | Many‑to‑One (related_name=`readiness_levels`) |
  | `type` | `CharField(10)` | No | – | – | Choices: `TRL`, `CRL` |
  | `level` | `IntegerField` | No | – | – | 1-9 |
  | `title` | `CharField(255)` | No | – | – | – |
  | `subtitle` | `CharField(255)` | Yes | – | – | – |

  #### Modelo: `Evidence`
  | Column | Type | Null | PK | FK | Relationship |
  |--------|------|------|----|----|--------------|
  | `id` | `AutoField` | No | Yes | – | – |
  | `startup_id` | `ForeignKey → Startup` | No | – | Yes | Many‑to‑One (related_name=`evidences`) |
  | `type` | `CharField(10)` | No | – | – | Choices: `TRL`, `CRL` |
  | `level` | `IntegerField` | No | – | – | – |
  | `description` | `TextField` | Yes | – | – | – |
  | `file_url` | `URLField` | Yes | – | – | – |
  | `status` | `CharField(20)` | No | – | – | Choices: `PENDING`, `APPROVED`, `REJECTED` |
  | `reviewer_notes` | `TextField` | Yes | – | – | – |

  #### Modelo: `FinancialInput`
  | Column | Type | Null | PK | FK | Notes |
  |--------|------|------|----|----|-------|
  | `id` | `AutoField` | No | Yes | – | – |
  | `startup_id` | `ForeignKey → Startup` | No | – | Yes | Many‑to‑One (related_name=`financial_inputs`) |
  | `period_date` | `DateField` | No | – | – | – |
  | `revenue` | `DecimalField(15,2)` | No | – | – | – |
  | `costs` | `DecimalField(15,2)` | No | – | – | – |
  | `cash_balance` | `DecimalField(15,2)` | No | – | – | – |
  | `monthly_burn` | `DecimalField(15,2)` | No | – | – | – |
  | `notes` | `TextField` | Yes | – | – | – |

  ### 1.3 Campaigns App (`campaigns/models.py`)
  | Table | Column | Type | Null | Primary Key | Foreign Key | Relationship |
  |-------|--------|------|------|-------------|-------------|--------------|
  | `Campaign` | `id` | `AutoField` | No | Yes | – | – |
  | | `startup_id` | `OneToOneField` → `users.Startup` (related_name=`campaign`) | No | – | – | One‑to‑One (each startup has one campaign). |
  | | `problem` | `TextField` | Yes | – | – |
  | | `solution` | `TextField` | Yes | – | – |
  | | `business_model` | `TextField` | Yes | – | – |
  | | `status` | `CharField(20)` (choices DRAFT, SUBMITTED, APPROVED, REJECTED) | No | – | – |
  | `InvestmentRound` | `id` | `AutoField` | No | Yes | – | – |
  | | `campaign_id` | `ForeignKey` → `Campaign` (related_name=`rounds`) | No | – | – | Many‑to‑One (campaign → rounds). |
  | | `name` | `CharField(100)` | No | – | – |
  | | `target_amount` | `DecimalField(12,2)` | No | – | – |
  | | `pre_money_valuation` | `DecimalField(15,2)` | Yes | – | – |
  | | `status` | `CharField(20)` (choices PLANNED, OPEN, CLOSED) | No | – | – |
  | | `is_current` | `BooleanField` (default=False) | No | – | – |
  | | `launch_date` | `DateField` | Yes | – | – | Date when the round officially opened. |
  | | `target_close_date` | `DateField` | Yes | – | – | Target deadline communicated to investors. |
  | | `actual_close_date` | `DateField` | Yes | – | – | Date when the round was actually closed. |
  | `Investor` (for a round) | `id` | `AutoField` | No | Yes | – | – |
  | | `round_id` | `ForeignKey` → `InvestmentRound` (related_name=`investors`) | No | – | – |
  | | `incubator_id` | `ForeignKey` → `users.Incubator` (related_name=`investments`) | No | – | – |
  | | `status` | `CharField(20)` (choices CONTACTED, PITCH_SENT, MEETING_SCHEDULED, DUE_DILIGENCE, TERM_SHEET, COMMITTED) | No | – | – |
  | | `amount` | `DecimalField(12,2)` | No | – | – |

  | `CampaignTeamMember` | `id` | `AutoField` | No | Yes | – | – |
  | | `campaign_id` | `ForeignKey` → `Campaign` (related_name=`team_members`) | No | – | – |
  | | `name` | `CharField(255)` | No | – | – |
  | | `role` | `CharField(255)` | No | – | – |
  | | `linkedin` | `URLField` | Yes | – | – |
  | | `avatar_url` | `URLField` | Yes | – | – |
  | `CampaignFinancials` | `id` | `AutoField` | No | Yes | – | – |
  | | `campaign_id` | `OneToOneField` → `Campaign` (related_name=`financials`) | No | – | – |
  | | `funding_goal` | `DecimalField(12,2)` | Yes | – | – |
  | | `valuation` | `DecimalField(12,2)` | Yes | – | – |
  | | `usage_of_funds` | `JSONField` (default=dict) | No | – | – |
  | | `revenue_history` | `JSONField` (default=dict) | No | – | – |
  | | `total_capital_injection` | `DecimalField` (calculated) | Yes | – | – | Sum of all committed investments. |
  | | `pre_money_valuation` | `DecimalField(15,2)` | Yes | – | – |
  | | `current_cash_balance` | `DecimalField(15,2)` | Yes | – | – |
  | | `monthly_burn_rate` | `DecimalField(15,2)` | Yes | – | – |
  | | `financial_projections` | `JSONField` (default=dict) | No | – | – |
  | `CampaignTraction` | `id` | `AutoField` | No | Yes | – | – |
  | | `campaign_id` | `ForeignKey` → `Campaign` (related_name=`tractions`) | No | – | – |
  | | `metrics` | `JSONField` (default=dict) | No | – | – |
  | | `proof_doc_url` | `URLField` | Yes | – | – |
  | `CampaignLegal` | `id` | `AutoField` | No | Yes | – | – |
  | | `campaign_id` | `OneToOneField` → `Campaign` (related_name=`legal`) | No | – | – |
  | | `constitution_url` | `URLField` | Yes | – | – |
  | | `whitepaper_url` | `URLField` | Yes | – | – |
  | | `cap_table_url` | `URLField` | Yes | – | – | – |

#### Modelo: `FinancialSheet`
| Column | Type | Null | PK | FK | Relationship |
|--------|------|------|----|----|--------------|
| `id` | `AutoField` | No | Yes | – | – |
| `campaign_id` | `OneToOneField → Campaign` | No | – | Yes | One‑to‑One |
| `sheet_data` | `JSONField` | No | – | – | Stores config, grid_rows (metrics, values, formulas) |

  ---

  ## 2. API Endpoints
  ### 2.1 Users App (`users/urls.py`)
  | Method | Path | View / ViewSet | Description |
  |--------|------|----------------|-------------|
  | **POST** | `/auth/registration/` | `dj_rest_auth.registration` | Register a new user (email/password). |
  | **POST** | `/auth/login/` | `dj_rest_auth` | Obtain JWT tokens. |
  | **POST** | `/auth/logout/` | `dj_rest_auth` | Logout (blacklist refresh token). |
  | **POST** | `/auth/password/reset/` | `dj_rest_auth` | Request password reset email. |
  | **POST** | `/auth/password/reset/confirm/` | `dj_rest_auth` | Confirm password reset. |
  | **POST** | `/auth/registration/account-confirm-email/` | `CustomVerifyEmailView` | Verify email and receive JWT tokens. |
  | **POST** | `/resend-email-confirmation/` | `ResendEmailConfirmationView` | Resend verification email (requires token). |
  | **POST** | `/reset-password/<uidb64>/<token>/` | `PasswordResetConfirmView` | Render password reset page (HTML). |
  | **GET** | `/onboarding/startup/` | `StartupOnboardingView.get` | Retrieve current startup profile & onboarding status. |
  | **POST** | `/onboarding/startup/` | `StartupOnboardingView.post` | Complete startup onboarding (company_name, industry). |
  | **POST** | `/startup/complete-onboarding/` | `OnboardingCompleteView` | Finalize wizard, create evidences and incubator associations. Only sends completed fields. |
  | **GET** | `/startup/data/` | `StartupDataView` | Return startup details (incl. computed `current_trl`, `current_crl`, `actual_revenue`). |
  | **GET** | `/startup/financial-data/` | `FinancialDataListView` | List all `FinancialInput` records for the startup. |
  | **GET** | `/startup/investors/` | `InvestorPipelineListView` | List all investor pipeline entries. |
  | **GET/POST/PUT/PATCH/DELETE** | `/startup/rounds/` | `RoundViewSet` (router) | CRUD for `Round` objects. |
  | **GET/POST/PUT/PATCH/DELETE** | `/startup/evidences/` | `EvidenceViewSet` (router) | CRUD for `Evidence` objects. |
  | **GET/POST/PUT/PATCH/DELETE** | `/startup/readiness-levels/` | `ReadinessLevelViewSet` (router) | CRUD for `ReadinessLevel` objects (TRL/CRL metadata). |
| **GET** | `/startup/associate-incubator/` | `StartupIncubatorAssociationViewSet` | List incubators associated with the startup. |
| **POST** | `/startup/associate-incubator/associate/` | `StartupIncubatorAssociationViewSet` | Associate startup with incubators (returns updated list). |
| **GET/POST/PUT/PATCH/DELETE** | `/incubators/` | `IncubatorViewSet` (router) | CRUD for Incubators. |
| **GET** | `/incubators/list_all/` | `IncubatorViewSet` (action) | Get ALL incubators (for selection). |
| **GET** | `/incubators/{id}/data/` | `IncubatorViewSet` (action) | Get consolidated incubator data (incl. portfolio startups). |
| **GET** | `/incubators/{id}/startups/` | `IncubatorViewSet` (action) | Get associated startups. |
| **GET/POST/PUT/PATCH/DELETE** | `/incubator/members/` | `IncubatorMemberViewSet` (router) | CRUD for Investors/Mentors. |
| **GET** | `/incubator/investments/` | `IncubatorInvestmentViewSet` (router) | List all investments (deals) for the incubator. |
| **POST** | `/incubator/investments/{id}/commit/` | `IncubatorInvestmentViewSet` (action) | Change investment status to `COMMITTED`. |
| **GET/POST/PUT/PATCH/DELETE** | `/challenges/` | `ChallengeViewSet` (router) | CRUD for Challenges. |
| **POST** | `/challenges/{id}/close/` | `ChallengeViewSet` (action) | Close a challenge. |
| **GET/POST/PUT/PATCH/DELETE** | `/challenge-applications/` | `ChallengeApplicationViewSet` (router) | Apply to challenges. |
| **GET** | `/incubator/portfolio/evidences/` | `PortfolioEvidenceViewSet` (router) | List all evidences from portfolio startups. |
| **POST** | `/incubator/portfolio/evidences/{id}/review/` | `PortfolioEvidenceViewSet` (action) | Approve or reject an evidence. |
| **GET** | `/incubator/portfolio/readiness-levels/` | `PortfolioReadinessLevelViewSet` (router) | List all readiness levels from portfolio startups. |
| **GET** | `/incubator/portfolio/campaigns/` | `PortfolioCampaignViewSet` (router) | List all campaigns with financials from portfolio startups. |

  ### 2.2 Campaigns App (`campaigns/urls.py`)
  | Method | Path | ViewSet | Description |
  |--------|------|---------|-------------|
  | **GET/POST/PUT/PATCH/DELETE** | `/campaigns/` | `CampaignViewSet` (router) | CRUD for `Campaign` objects (one per startup). |
  | **GET** | `/campaigns/my-campaign/` | `CampaignViewSet` (action) | Get current user's campaign (auto-creates). |
  | **POST** | `/campaigns/{id}/submit/` | `CampaignViewSet` (action) | Submit campaign for review. |
  | **GET/PATCH** | `/campaigns/{id}/financials/` | `CampaignViewSet` (action) | Get or update campaign financials. |
  | **GET** | `/campaigns/startup/{startup_id}/` | `CampaignViewSet` (action) | Get campaign by startup ID (for incubators). |

  ---

  ## 3. Request / Response Schemas & Axios TypeScript Examples
  ### 3.0 Authentication (Registration & Verification)
  #### Register (POST `/auth/registration/`)
  **Request**
  ```json
  {
    "email": "user@example.com",
    "password1": "securePassword123",
    "password2": "securePassword123",
    "user_type": "startup",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
  **Response**
  ```json
  {
    "detail": "Verification e-mail sent."
  }
  ```
  **Axios TS**
  ```ts
  import axios from 'axios';

  export interface RegisterDTO {
    email: string;
    password1: string;
    password2: string;
    user_type: 'startup' | 'incubator';
    first_name?: string;
    last_name?: string;
  }

  export const register = async (data: RegisterDTO) => {
    const resp = await axios.post('/auth/registration/', data);
    return resp.data;
  };
  ```

  #### Verify Email (POST `/auth/registration/account-confirm-email/`)
  **Request**
  ```json
  {
    "key": "Mg.X7... (verification key from email)"
  }
  ```
  **Response**
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "detail": "Email verified successfully. You are now logged in."
  }
  ```
  **Axios TS**
  ```ts
  export const verifyEmail = async (key: string) => {
    const resp = await axios.post('/auth/registration/account-confirm-email/', { key });
    // Store tokens
    localStorage.setItem('access', resp.data.access_token);
    localStorage.setItem('refresh', resp.data.refresh_token);
    return resp.data;
  };
  ```

  ### 3.1 Onboarding Wizard (POST `/startup/complete-onboarding/`)
  **Important**: The frontend now sends **only the fields that the user completed** in the wizard. Optional fields (`evidences`, `incubator_ids`) are only sent if they contain data.

  **Required Fields**:
  - `company_name` (string, max 255 chars)
  - `industry` (string, max 50 chars)
  - `current_trl` (integer, 1-9)

  **Optional Fields**:
  - `current_crl` (integer, 1-9, nullable)
  - `readiness_levels` (array of readiness level objects)
  - `evidences` (array of evidence objects - legacy)
  - `incubator_ids` (array of incubator IDs)

  #### Example: Minimal Request (Only Basic Info)
  ```json
  {
    "company_name": "Startup Inc",
    "industry": "technology",
    "current_trl": 3,
    "current_crl": null
  }
  ```

  #### Example: With Readiness Levels
  ```json
  {
    "company_name": "Startup Inc",
    "industry": "technology",
    "current_trl": 3,
    "current_crl": 2,
    "readiness_levels": [
      {
        "type": "TRL",
        "level": 3,
        "title": "Working Prototype",
        "subtitle": "Lab validation complete",
        "evidences": [
          {
            "description": "Prototype demonstrated successfully",
            "file_url": "https://storage.example.com/demo.mp4"
          }
        ]
      }
    ]
  }
  ```

  #### Example: Complete Request
  ```json
  {
    "company_name": "Startup Inc",
    "industry": "technology",
    "current_trl": 3,
    "current_crl": 2,
    "readiness_levels": [
      {
        "type": "TRL",
        "level": 3,
        "title": "Working Prototype",
        "evidences": [
          {
            "description": "Prototype demonstrated successfully"
          }
        ]
      }
    ],
    "incubator_ids": [1, 2]
  }
  ```

  **Response** (201 Created)
  ```json
  {
    "detail": "Onboarding wizard completed successfully",
    "startup_id": 5,
    "current_trl": 3,
    "current_crl": 2,
    "readiness_levels_count": 1,
    "evidences_count": 1,
    "incubators_count": 2
  }
  ```

  **Axios TS**
  ```ts
  export interface EvidenceDTO {
    description?: string;
    file_url?: string;
  }

  export interface ReadinessLevelDTO {
    type: 'TRL' | 'CRL';
    level: number;
    title: string;
    subtitle?: string;
    evidences?: EvidenceDTO[];
  }

  export interface OnboardingWizardDTO {
    company_name: string;
    industry: string;
    current_trl: number;
    current_crl?: number | null;
    readiness_levels?: ReadinessLevelDTO[];
    incubator_ids?: number[];
  }

  export interface OnboardingResponseDTO {
    detail: string;
    startup_id: number;
    current_trl: number;
    current_crl?: number;
    readiness_levels_count: number;
    evidences_count: number;
    incubators_count: number;
  }

  export const completeOnboarding = async (
    token: string,
    data: OnboardingWizardDTO
  ): Promise<OnboardingResponseDTO> => {
    const resp = await axios.post<OnboardingResponseDTO>(
      '/startup/complete-onboarding/',
      data,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return resp.data;
  };
  ```

  ### 3.1.1 Incubator Onboarding (POST `/incubator/complete-onboarding/`)
  **Request**
  ```json
  {
    "name": "Y Combinator",
    "description": "We help startups launch.",
    "logo_url": "https://storage.googleapis.com/.../yc-logo.png"
  }
  ```
  **Response** (200 OK)
  ```json
  {
    "detail": "Onboarding completed successfully.",
    "incubator": {
      "id": 1,
      "name": "Y Combinator",
      "description": "We help startups launch.",
      "logo_url": "https://storage.googleapis.com/.../yc-logo.png",
      "profile_complete": true,
      "members": [],
      "startups": [],
      "created": "2024-11-01T10:00:00Z",
      "updated": "2024-11-01T10:00:00Z"
    }
  }
  ```
  **Axios TS**
  ```ts
  export interface IncubatorOnboardingDTO {
    name: string;
    description?: string;
    logo_url?: string;
  }

  export const completeIncubatorOnboarding = async (token: string, data: IncubatorOnboardingDTO) => {
    const resp = await axios.post('/incubator/complete-onboarding/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ### 3.1.2 Get Incubator Data (GET `/incubator/data/`)
  **Request**
  ```http
  GET /incubator/data/ HTTP/1.1
  Authorization: Bearer <access_token>
  ```
  **Response** (200 OK)
  ```json
  {
    "id": 1,
    "name": "Y Combinator",
    "description": "We help startups launch.",
    "logo_url": "https://storage.googleapis.com/.../yc-logo.png",
    "profile_complete": true,
    "members": [],
    "startups": [],
    "portfolio_startups": [],
    "created": "2024-11-01T10:00:00Z",
    "updated": "2024-11-01T10:00:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export const fetchMyIncubatorData = async (token: string): Promise<IncubatorDTO> => {
    const resp = await axios.get<IncubatorDTO>('/incubator/data/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ### 3.2 Authentication (Login)
  **Request** (`POST /auth/login/`)
  ```json
  {
    "email": "user@example.com",
    "password": "securePassword123"
  }
  ```
  **Response**
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
  ```
  **Axios TS**
  ```ts
  import axios from 'axios';

  interface LoginResponse {
    access_token: string;
    refresh_token: string;
  }

  export const login = async (email: string, password: string) => {
    const resp = await axios.post<LoginResponse>('/auth/login/', { email, password });
    // Store tokens (e.g., localStorage) for subsequent calls
    localStorage.setItem('access', resp.data.access_token);
    localStorage.setItem('refresh', resp.data.refresh_token);
    return resp.data;
  };
  ```
  ---
  ### 3.3 Get Startup Data
  **Request** (`GET /startup/data/` with Authorization header)
  ```http
  GET /startup/data/ HTTP/1.1
  Authorization: Bearer <access_token>
  ```
  **Response** (excerpt)
  ```json
  {
    "id": 3,
    "company_name": "Acme Corp",
    "industry": "technology",
    "logo_url": "https://storage.googleapis.com/.../logo.png",
    "created": "2024-11-01T12:34:56Z",
    "updated": "2025-01-15T08:20:10Z",
    "TRL_level": 4,
    "CRL_level": 2,
    "actual_revenue": 125000.00,
    "incubators": [
      {
        "id": 1,
        "name": "Y Combinator",
        "created": "2024-11-01T10:00:00Z",
        "updated": "2024-11-01T10:00:00Z"
      }
    ]
  }
  ```
  **Axios TS**
  ```ts
  import axios from 'axios';

  export interface StartupDTO {
    id: number;
    company_name: string;
    industry: string;
    logo_url?: string;
    created: string; // ISO date
    updated: string;
    TRL_level?: number;
    CRL_level?: number;
    actual_revenue?: number;
    incubators?: IncubatorDTO[];
  }

  export const fetchStartup = async (token: string): Promise<StartupDTO> => {
    const resp = await axios.get<StartupDTO>('/startup/data/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```
  ---
  ### 3.4 Create Evidence (POST `/startup/evidences/`)
  **Request**
  ```json
  {
    "type": "TRL",
    "level": 3,
    "description": "Prototype demonstrated to early adopters.",
    "file_url": "https://storage.googleapis.com/.../evidence.pdf",
    "status": "APPROVED"
  }
  ```
  **Response** (201)
  ```json
  {
    "id": 12,
    "type": "TRL",
    "level": 3,
    "description": "Prototype demonstrated to early adopters.",
    "file_url": "https://storage.googleapis.com/.../evidence.pdf",
    "status": "APPROVED",
    "reviewer_notes": null,
    "created": "2025-12-02T10:05:00Z",
    "updated": "2025-12-02T10:05:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export interface EvidenceCreateDTO {
    type: 'TRL' | 'CRL';
    level: number;
    description?: string;
    file_url?: string;
    status?: 'PENDING' | 'APPROVED' | 'REJECTED';
  }

  export const createEvidence = async (token: string, data: EvidenceCreateDTO) => {
    const resp = await axios.post<EvidenceCreateDTO & { id: number; created: string; updated: string }>(
      '/startup/evidences/',
      data,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return resp.data;
  };
  ```
  ---
  ### 3.5 List Financial Inputs (GET `/startup/financial-data/`)
  **Response** (array)
  ```json
  [
    {
      "id": 5,
      "period_date": "2024-01-31",
      "revenue": "5000.00",
      "costs": "8000.00",
      "cash_balance": "45000.00",
      "monthly_burn": "3000.00",
      "notes": null,
      "created": "2025-01-10T14:22:00Z",
      "updated": "2025-01-10T14:22:00Z"
    }
  ]
  ```
  **Axios TS**
  ```ts
  export interface FinancialInputDTO {
    id: number;
    period_date: string; // YYYY-MM-DD
    revenue: string; // decimal as string
    costs: string;
    cash_balance: string;
    monthly_burn: string;
    notes?: string;
    created: string;
    updated: string;
  }

  export const fetchFinancials = async (token: string): Promise<FinancialInputDTO[]> => {
    const resp = await axios.get<FinancialInputDTO[]>('/startup/financial-data/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```
  ---
  ### 3.6 Create Round (POST `/startup/rounds/`)
  **Request**
  ```json
  {
    "name": "Series A",
    "target_amount": "2000000.00",
    "pre_money_valuation": "10000000.00",
    "status": "OPEN",
    "is_current": true,
    "launch_date": "2025-03-01",
    "target_close_date": "2025-06-30",
    "investors": [
      {
        "incubator_id": 1,
        "amount": "50000.00",
        "status": "COMMITTED"
      }
    ]
  }
  ```
  **Response** (201)
  ```json
  {
    "id": 4,
    "name": "Series A",
    "target_amount": "2000000.00",
    "pre_money_valuation": "10000000.00",
    "status": "OPEN",
    "is_current": true,
    "launch_date": "2025-03-01",
    "target_close_date": "2025-06-30",
    "actual_close_date": null,
    "investors": [
      {
        "id": 10,
        "incubator_details": {
            "id": 1,
            "name": "Y Combinator"
        },
        "amount": "50000.00",
        "status": "COMMITTED"
      }
    ],
    "created": "2025-12-03T12:00:00Z",
    "updated": "2025-12-03T12:00:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export interface RoundCreateDTO {
    name: string;
    target_amount: string; // decimal string
    pre_money_valuation?: string;
    status?: 'PLANNED' | 'OPEN' | 'CLOSED';
    is_current?: boolean;
    launch_date?: string; // YYYY-MM-DD
    target_close_date?: string;
    actual_close_date?: string;
    investors?: InvestorDTO[];
  }

  export const createRound = async (token: string, data: RoundCreateDTO) => {
    const resp = await axios.post<InvestmentRoundDTO>(
      '/startup/rounds/',
      data,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return resp.data;
  };
  ```
  ---
  ### 3.7 Campaign CRUD (router `/campaigns/`)
  **GET** `/campaigns/` returns list of campaigns belonging to the authenticated startup.
  **POST** `/campaigns/` creates a new campaign (requires `startup` relationship is inferred from token).
  **Example POST payload**
  ```json
  {
    "problem": "We lack a scalable onboarding process.",
    "solution": "AI‑driven onboarding platform.",
    "business_model": "SaaS subscription",
    "status": "DRAFT"
  }
  ```
  **Axios TS**
  ```ts
  export interface CampaignDTO {
    id: number;
    problem?: string;
    solution?: string;
    business_model?: string;
    status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';
    created: string;
    updated: string;
  }

  export const createCampaign = async (token: string, data: Partial<CampaignDTO>) => {
    const resp = await axios.post<CampaignDTO>('/campaigns/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  ### 3.7.1 Investment Rounds (CRUD `/rounds/`)
  **GET/POST/PUT/PATCH/DELETE** `/rounds/` manages investment rounds for the startup's campaign.
  **PATCH/PUT** supports nested updates for `investors` (tickets).

  **Request (PATCH/PUT with nested investors)**
  ```json
  {
    "target_amount": "500000.00",
    "launch_date": "2025-01-01",
    "target_close_date": "2025-06-30",
    "investors": [
      {
        "id": 10,
        "incubator_id": 1,
        "amount": "50000.00",
        "status": "COMMITTED"
      },
      {
        "incubator_id": 2,
        "amount": "25000.00",
        "status": "CONTACTED"
      }
    ]
  }
  ```

  **Axios TS**
  ```ts
  export interface InvestorDTO {
    id?: number;
    incubator_id?: number; // Write-only (for creating/updating)
    incubator_details?: {  // Read-only
      id: number;
      name: string;
    };
    amount: string;
    status: 'CONTACTED' | 'PITCH_SENT' | 'MEETING_SCHEDULED' | 'DUE_DILIGENCE' | 'TERM_SHEET' | 'COMMITTED';
  }

  export interface InvestmentRoundDTO {
    id: number;
    name: string;
    target_amount: string;
    pre_money_valuation?: string;
    status: 'PLANNED' | 'OPEN' | 'CLOSED';
    is_current: boolean;
    launch_date?: string;
    target_close_date?: string;
    actual_close_date?: string;
    investors?: InvestorDTO[];
    total_committed_amount?: number;
    created: string;
    updated: string;
  }

  export const updateRound = async (token: string, id: number, data: Partial<InvestmentRoundDTO>) => {
    const resp = await axios.patch<InvestmentRoundDTO>(\`/rounds/\${id}/\`, data, {
      headers: { Authorization: \`Bearer \${token}\` },
    });
    return resp.data;
  };
  ```

  ### 3.8 Readiness Levels (CRUD `/startup/readiness-levels/`)
  **GET** `/startup/readiness-levels/` returns list of configured levels for the startup.
  **POST** `/startup/readiness-levels/` creates a new level definition.
  **DELETE** `/startup/readiness-levels/{id}/` deletes the level definition AND its associated evidence. Automatically recalculates the startup's TRL/CRL level (drops to the last continuous approved level).

  **Request (Create)**
  ```json
  {
    "type": "TRL",
    "level": 1,
    "title": "Basic Principles Observed",
    "subtitle": "Scientific research begins to be translated into applied research and development."
  }
  ```
  **Response** (201)
  ```json
  {
    "id": 1,
    "startup": 3,
    "type": "TRL",
    "level": 1,
    "title": "Basic Principles Observed",
    "subtitle": "Scientific research begins to be translated into applied research and development.",
    "created": "2025-12-03T18:30:00Z",
    "updated": "2025-12-03T18:30:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export interface ReadinessLevelDTO {
    id: number;
    type: 'TRL' | 'CRL';
    level: number;
    title: string;
    subtitle?: string;
    created: string;
    updated: string;
  }

  export const createReadinessLevel = async (token: string, data: Partial<ReadinessLevelDTO>) => {
    const resp = await axios.post<ReadinessLevelDTO>('/startup/readiness-levels/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  ### 3.9 Get Incubator Data (GET `/incubators/{id}/data/`)
  **Response**
  ```json
  {
    "id": 1,
    "name": "Y Combinator",
    "description": "We help startups launch.",
    "logo_url": "https://storage.googleapis.com/.../yc-logo.png",
    "profile_complete": true,
    "members": [],
    "startups": [],
    "portfolio_startups": [
      {
        "id": 3,
        "company_name": "Acme Corp",
        "logo_url": "https://storage.googleapis.com/.../logo.png",
        "industry": "technology"
      }
    ],
    "created": "2024-11-01T10:00:00Z",
    "updated": "2024-11-01T10:00:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export interface PortfolioStartupDTO {
    id: number;
    company_name: string;
    logo_url?: string;
    industry: string;
  }

  export interface IncubatorDTO {
    id: number;
    name: string;
    description?: string;
    logo_url?: string;
    profile_complete: boolean;
    portfolio_startups: PortfolioStartupDTO[];
    portfolio_summary?: {
      total_portfolio_target: number;
      total_portfolio_committed: number;
      average_trl: number;
    };
    created: string;
    updated: string;
  }

  export const fetchIncubatorData = async (token: string, id: number): Promise<IncubatorDTO> => {
    const resp = await axios.get<IncubatorDTO>(\`/incubators/\${id}/data/\`, {
      headers: { Authorization: \`Bearer \${token}\` },
    });
    return resp.data;
  };
  ```

  export const fetchReadinessLevels = async (token: string): Promise<ReadinessLevelDTO[]> => {
    const resp = await axios.get<ReadinessLevelDTO[]>('/startup/readiness-levels/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  ### 3.10 Incubator Members (CRUD `/incubator/members/`)
  **GET** `/incubator/members/` returns list of members for the authenticated incubator.
  **POST** `/incubator/members/` creates a new member.

  **Request (Create)**
  ```json
  {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+1234567890",
    "role": "MENTOR"
  }
  ```
  **Response** (201)
  ```json
  {
    "id": 1,
    "incubator": 1,
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+1234567890",
    "role": "MENTOR",
    "created": "2025-12-04T10:00:00Z",
    "updated": "2025-12-04T10:00:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export interface IncubatorMemberDTO {
    id: number;
    full_name: string;
    email: string;
    phone?: string;
    role: 'INVESTOR' | 'MENTOR' | 'BOTH';
    created: string;
    updated: string;
  }

  export const createIncubatorMember = async (token: string, data: Partial<IncubatorMemberDTO>) => {
    const resp = await axios.post<IncubatorMemberDTO>('/incubator/members/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ### 3.11 Challenges (CRUD `/challenges/`)
  **GET** `/challenges/` returns list of challenges (Incubator sees own, Startup sees open).
  **POST** `/challenges/` creates a new challenge (Incubator only).

  **Request (Create)**
  ```json
  {
    "title": "Fintech Innovation Challenge",
    "subtitle": "Revolutionizing payments",
    "description": "We are looking for...",
    "budget": "50000.00",
    "deadline": "2025-12-31",
    "required_technologies": "Blockchain, AI",
    "status": "OPEN"
  }
  ```
  **Response** (201)
  ```json
  {
    "id": 1,
    "incubator": 1,
    "title": "Fintech Innovation Challenge",
    "subtitle": "Revolutionizing payments",
    "description": "We are looking for...",
    "budget": "50000.00",
    "deadline": "2025-12-31",
    "required_technologies": "Blockchain, AI",
    "status": "OPEN",
    "applicant_count": 0,
    "created": "2025-12-04T10:00:00Z",
    "updated": "2025-12-04T10:00:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export interface ChallengeDTO {
    id: number;
    title: string;
    subtitle?: string;
    description: string;
    budget?: string;
    deadline?: string;
    required_technologies: string;
    status: 'OPEN' | 'CONCLUDED';
    applicant_count: number;
    created: string;
    updated: string;
  }

  export const createChallenge = async (token: string, data: Partial<ChallengeDTO>) => {
    const resp = await axios.post<ChallengeDTO>('/challenges/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ### 3.12 Challenge Applications (CRUD `/challenge-applications/`)
  **POST** `/challenge-applications/` apply to a challenge (Startup only).

  **Request (Create)**
  ```json
  {
    "challenge": 1,
    "text_solution": "Our solution uses..."
  }
  ```
  **Response** (201)
  ```json
  {
    "id": 1,
    "challenge": 1,
    "startup": 3,
    "startup_name": "Acme Corp",
    "text_solution": "Our solution uses...",
    "created": "2025-12-04T10:00:00Z",
    "updated": "2025-12-04T10:00:00Z"
  }
  ```
  **Axios TS**
  ```ts
  export interface ChallengeApplicationDTO {
    id: number;
    challenge: number;
    startup: number;
    startup_name: string;
    text_solution: string;
    created: string;
    updated: string;
  }

  export const applyToChallenge = async (token: string, data: Partial<ChallengeApplicationDTO>) => {
    const resp = await axios.post<ChallengeApplicationDTO>('/challenge-applications/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ### 3.13 Associate Incubator (POST `/startup/associate-incubator/associate/`)
  **Request**
  ```json
  {
    "incubator_ids": [1, 2]
  }
  ```
  **Response** (200)
  ```json
  [
    {
      "id": 1,
      "name": "Y Combinator",
      "logo_url": "...",
      "industry": "technology",
      "profile_complete": true,
      "members": [],
      "startups": [],
      "portfolio_startups": [],
      "created": "...",
      "updated": "..."
    },
    {
      "id": 2,
      "name": "Techstars",
      "logo_url": "...",
      "industry": "technology",
      "profile_complete": true,
      "members": [],
      "startups": [],
      "portfolio_startups": [],
      "created": "...",
      "updated": "..."
    }
  ]
  ```
  **Axios TS**
  ```ts
  export const associateIncubators = async (token: string, incubatorIds: number[]) => {
    const resp = await axios.post<IncubatorDTO[]>('/startup/associate-incubator/associate/', 
      { incubator_ids: incubatorIds },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return resp.data;
  };
  ```

  export const deleteReadinessLevel = async (token: string, id: number) => {
    await axios.delete(`/startup/readiness-levels/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  };
  ```
  ---
### 3.9 Startup Incubator Association (`/startup/associate-incubator/`)
  #### List Associated Incubators (GET `/startup/associate-incubator/`)
  **Response** (array of Incubator objects)
  ```json
  [
    {
      "id": 1,
      "name": "Y Combinator",
      "created": "2024-11-01T10:00:00Z",
      "updated": "2024-11-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Techstars",
      "created": "2024-11-02T11:00:00Z",
      "updated": "2024-11-02T11:00:00Z"
    }
  ]
  ```
  **Axios TS**
  ```ts
  export interface IncubatorDTO {
    id: number;
    name: string;
    created: string;
    updated: string;
    startups?: Array<{
      id: number;
      company_name: string;
      logo_url?: string;
      industry?: string;
    }>;
  }

  export const fetchAssociatedIncubators = async (token: string): Promise<IncubatorDTO[]> => {
    const resp = await axios.get<IncubatorDTO[]>('/startup/associate-incubator/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  #### Update Incubator Associations (POST `/startup/associate-incubator/associate/`)
  **Request**
  ```json
  {
    "incubator_ids": [1, 3]
  }
  ```
  **Response** (updated array of Incubator objects)
  ```json
  [
    {
      "id": 1,
      "name": "Y Combinator",
      "created": "2024-11-01T10:00:00Z",
      "updated": "2024-11-01T10:00:00Z"
    },
    {
      "id": 3,
      "name": "500 Startups",
      "created": "2024-11-03T12:00:00Z",
      "updated": "2024-11-03T12:00:00Z"
    }
  ]
  ```
  **Axios TS**
  ```ts
  export const updateIncubatorAssociations = async (
    token: string,
    incubatorIds: number[]
  ): Promise<IncubatorDTO[]> => {
    const resp = await axios.post<IncubatorDTO[]>(
      '/startup/associate-incubator/associate/',
      { incubator_ids: incubatorIds },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return resp.data;
  };
  ```

  ---

  ### 3.14 Incubator Investments (CRUD `/incubator/investments/`)
  **GET** `/incubator/investments/` returns list of investments (deals) for the authenticated incubator.
  **POST** `/incubator/investments/{id}/commit/` changes the status of an investment to `COMMITTED`.

  **Response (List)**
  ```json
  [
    {
      "id": 10,
      "round": 4,
      "round_name": "Series A",
      "startup_id": 3,
      "startup_name": "Acme Corp",
      "logo_url": "https://storage.googleapis.com/.../logo.png",
      "amount": "50000.00",
      "status": "CONTACTED",
      "created": "2025-12-04T10:00:00Z",
      "updated": "2025-12-04T10:00:00Z"
    }
  ]
  ```

  **Request (Commit)**
  ```http
  POST /incubator/investments/10/commit/ HTTP/1.1
  Authorization: Bearer <access_token>
  ```

  **Response (Commit)**
  ```json
  {
    "id": 10,
    "round": 4,
    "round_name": "Series A",
    "startup_id": 3,
    "startup_name": "Acme Corp",
    "logo_url": "https://storage.googleapis.com/.../logo.png",
    "amount": "50000.00",
    "status": "COMMITTED",
    "created": "2025-12-04T10:00:00Z",
    "updated": "2025-12-04T10:05:00Z"
  }
  ```

  **Axios TS**
  ```ts
  export interface IncubatorInvestmentDTO {
    id: number;
    round: number;
    round_name: string;
    startup_id: number;
    startup_name: string;
    logo_url?: string;
    amount: string;
    status: 'CONTACTED' | 'PITCH_SENT' | 'MEETING_SCHEDULED' | 'DUE_DILIGENCE' | 'TERM_SHEET' | 'COMMITTED';
    created: string;
    updated: string;
  }

  export const fetchIncubatorInvestments = async (token: string): Promise<IncubatorInvestmentDTO[]> => {
    const resp = await axios.get<IncubatorInvestmentDTO[]>('/incubator/investments/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const commitInvestment = async (token: string, id: number): Promise<IncubatorInvestmentDTO> => {
    const resp = await axios.post<IncubatorInvestmentDTO>(`/incubator/investments/${id}/commit/`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ---

  ### 3.15 Challenges (CRUD `/challenges/`)
  **GET** `/challenges/` returns list of challenges.
  - **Incubators**: Returns only challenges created by the authenticated incubator.
  - **Startups**: Returns all challenges with status `OPEN`.

  **POST** `/challenges/` creates a new challenge (Incubator only).
  **PATCH** `/challenges/{id}/` updates a challenge (e.g., changing status).

  **Response (List)**
  ```json
  [
    {
      "id": 1,
      "incubator": 1,
      "title": "Fintech Innovation Challenge",
      "subtitle": "Revolutionizing payments",
      "description": "We are looking for...",
      "budget": "50000.00",
      "deadline": "2025-12-31",
      "required_technologies": "Blockchain, AI",
      "status": "OPEN",
      "applicant_count": 5,
      "created": "2025-12-04T10:00:00Z",
      "updated": "2025-12-04T10:00:00Z"
    }
  ]
  ```

  **Request (Create)**
  ```json
  {
    "title": "AI in Healthcare",
    "subtitle": "Improving diagnostics",
    "description": "Seeking startups using AI for early detection...",
    "budget": "100000.00",
    "deadline": "2026-06-30",
    "required_technologies": "Python, TensorFlow, PyTorch",
    "status": "OPEN"
  }
  ```

  **Request (PATCH - Change Status)**
  ```http
  PATCH /challenges/1/ HTTP/1.1
  Authorization: Bearer <access_token>
  Content-Type: application/json

  {
    "status": "CONCLUDED"
  }
  ```

  **Response (Update)**
  ```json
  {
    "id": 1,
    "incubator": 1,
    "title": "Fintech Innovation Challenge",
    "status": "CONCLUDED",
    "updated": "2025-12-04T12:00:00Z",
    ...
  }
  ```

  **Axios TS**
  ```ts
  export interface ChallengeDTO {
    id: number;
    incubator: number;
    title: string;
    subtitle?: string;
    description: string;
    budget?: string;
    deadline?: string;
    required_technologies: string;
    status: 'OPEN' | 'CONCLUDED';
    applicant_count: number;
    created: string;
    updated: string;
  }

  export const fetchChallenges = async (token: string): Promise<ChallengeDTO[]> => {
    const resp = await axios.get<ChallengeDTO[]>('/challenges/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const createChallenge = async (token: string, data: Partial<ChallengeDTO>): Promise<ChallengeDTO> => {
    const resp = await axios.post<ChallengeDTO>('/challenges/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const updateChallengeStatus = async (token: string, id: number, status: 'OPEN' | 'CONCLUDED'): Promise<ChallengeDTO> => {
    const resp = await axios.patch<ChallengeDTO>(`/challenges/${id}/`, { status }, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ---

  ### 3.16 Challenge Applications (CRUD `/challenge-applications/`)
  **GET** `/challenge-applications/` returns list of applications.
  - **Incubators**: Returns all applications received for ANY of their challenges.
  - **Startups**: Returns only applications they have submitted.

  **POST** `/challenge-applications/` apply to a challenge (Startup only).

  **Response (List - Incubator View)**
  ```json
  [
    {
      "id": 10,
      "challenge": 1,
      "startup": 3,
      "startup_name": "Acme Corp",
      "text_solution": "We propose using our AI engine...",
      "created": "2025-12-05T14:30:00Z",
      "updated": "2025-12-05T14:30:00Z"
    }
  ]
  ```

  **Request (Create - Startup)**
  ```json
  {
    "challenge": 1,
    "text_solution": "Our solution involves..."
  }
  ```

  **Axios TS**
  ```ts
  export interface ChallengeApplicationDTO {
    id: number;
    challenge: number;
    startup: number;
    startup_name: string;
    text_solution: string;
    created: string;
    updated: string;
  }

  export const fetchChallengeApplications = async (token: string): Promise<ChallengeApplicationDTO[]> => {
    const resp = await axios.get<ChallengeApplicationDTO[]>('/challenge-applications/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const applyToChallenge = async (token: string, data: Partial<ChallengeApplicationDTO>): Promise<ChallengeApplicationDTO> => {
    const resp = await axios.post<ChallengeApplicationDTO>('/challenge-applications/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ---

  ## 4. Audit Dashboard Metrics (Financial & Portfolio)

  ### 4.1 Startup Financials (Capital Injection for VAN/TIR)
  **Endpoint:** `GET /campaigns/my-campaign/`
  **Key Field:** `financials.total_capital_injection`
  **Usage:** Use this value as the initial investment (negative cash flow at t=0) for VAN/TIR calculations. It represents the sum of all **COMMITTED** investments across all rounds.

  **Response Snippet**
  ```json
  {
    "id": 1,
    "status": "DRAFT",
    "financials": {
      "funding_goal": "500000.00",
      "total_capital_injection": 150000.00,  // <--- USE THIS FOR VAN/TIR
      "pre_money_valuation": "2000000.00",
      ...
    },
    "rounds": [
      {
        "id": 1,
        "name": "Pre-Seed",
        "total_committed_amount": 50000.00,
        "investors": [...]
      },
      {
        "id": 2,
        "name": "Seed",
        "total_committed_amount": 100000.00,
        "investors": [...]
      }
    ]
  }
  ```

  ### 4.2 Incubator Portfolio Summary
  **Endpoint:** `GET /incubators/{id}/data/`
  **Key Field:** `portfolio_summary`
  **Usage:** Provides aggregated metrics for the incubator's dashboard.

  **Response Snippet**
  ```json
  {
    "id": 1,
    "name": "Y Combinator",
    "portfolio_summary": {
      "total_portfolio_target": 5000000.00,      // Sum of all startups' funding goals
      "total_portfolio_committed": 1250000.00,   // Sum of all startups' committed capital
      "average_trl": 4.5                         // Average TRL level
    },
    "portfolio_startups": [
      {
        "id": 3,
        "company_name": "Acme Corp",
        "industry": "Fintech"
      },
      ...
    ]
  }
  ```

  **Axios TS Interfaces**
  ```ts
  export interface PortfolioSummaryDTO {
    total_portfolio_target: number;
    total_portfolio_committed: number;
    average_trl: number;
  }

  export interface IncubatorDataDTO {
    id: number;
    name: string;
    portfolio_summary: PortfolioSummaryDTO;
    portfolio_startups: PortfolioStartupDTO[];
    // ... other fields
  }
  ```

  ---

  ### 4.3 Portfolio Evidence Review (Incubator)
  **Endpoints:**
  - `GET /incubator/portfolio/evidences/` - List all evidences from portfolio startups.
  - `GET /incubator/portfolio/evidences/{id}/` - Get a single evidence detail.
  - `POST /incubator/portfolio/evidences/{id}/review/` - Approve or reject an evidence.
  - `GET /incubator/portfolio/readiness-levels/` - List all readiness levels with nested evidences.

  **Response (List Evidences)**
  ```json
  [
    {
      "id": 15,
      "startup_id": 3,
      "startup_name": "Acme Corp",
      "startup_logo": "https://storage.googleapis.com/.../logo.png",
      "type": "TRL",
      "level": 4,
      "description": "Prototype validated in lab environment",
      "file_url": "https://storage.googleapis.com/.../evidence.pdf",
      "status": "PENDING",
      "reviewer_notes": null,
      "created": "2025-12-01T10:00:00Z",
      "updated": "2025-12-01T10:00:00Z"
    }
  ]
  ```

  **Request (Review Evidence)**
  ```http
  POST /incubator/portfolio/evidences/15/review/ HTTP/1.1
  Authorization: Bearer <access_token>
  Content-Type: application/json

  {
    "status": "APPROVED",
    "reviewer_notes": "Evidence meets the criteria for TRL 4."
  }
  ```

  **Response (Review)**
  ```json
  {
    "id": 15,
    "startup_id": 3,
    "startup_name": "Acme Corp",
    "startup_logo": "https://storage.googleapis.com/.../logo.png",
    "type": "TRL",
    "level": 4,
    "description": "Prototype validated in lab environment",
    "file_url": "https://storage.googleapis.com/.../evidence.pdf",
    "status": "APPROVED",
    "reviewer_notes": "Evidence meets the criteria for TRL 4.",
    "created": "2025-12-01T10:00:00Z",
    "updated": "2025-12-04T08:50:00Z"
  }
  ```

  **Response (List Readiness Levels)**
  ```json
  [
    {
      "id": 10,
      "startup_id": 3,
      "startup_name": "Acme Corp",
      "type": "TRL",
      "level": 4,
      "title": "Component Validation",
      "subtitle": "Technology validated in lab",
      "evidences": [
        {
          "id": 15,
          "status": "PENDING",
          ...
        }
      ],
      "created": "2025-12-01T10:00:00Z",
      "updated": "2025-12-01T10:00:00Z"
    }
  ]
  ```

  **Axios TS Interfaces**
  ```ts
  export interface PortfolioEvidenceDTO {
    id: number;
    startup_id: number;
    startup_name: string;
    startup_logo?: string;
    type: 'TRL' | 'CRL';
    level: number;
    description?: string;
    file_url?: string;
    status: 'PENDING' | 'APPROVED' | 'REJECTED';
    reviewer_notes?: string;
    created: string;
    updated: string;
  }

  export interface EvidenceReviewDTO {
    status: 'APPROVED' | 'REJECTED';
    reviewer_notes?: string;
  }

  export interface PortfolioReadinessLevelDTO {
    id: number;
    startup_id: number;
    startup_name: string;
    type: 'TRL' | 'CRL';
    level: number;
    title: string;
    subtitle?: string;
    evidences: PortfolioEvidenceDTO[];
    created: string;
    updated: string;
  }

  export const fetchPortfolioEvidences = async (token: string): Promise<PortfolioEvidenceDTO[]> => {
    const resp = await axios.get<PortfolioEvidenceDTO[]>('/incubator/portfolio/evidences/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const reviewEvidence = async (
    token: string, 
    id: number, 
    data: EvidenceReviewDTO
  ): Promise<PortfolioEvidenceDTO> => {
    const resp = await axios.post<PortfolioEvidenceDTO>(
      `/incubator/portfolio/evidences/${id}/review/`, 
      data,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return resp.data;
  };

  export const fetchPortfolioReadinessLevels = async (token: string): Promise<PortfolioReadinessLevelDTO[]> => {
    const resp = await axios.get<PortfolioReadinessLevelDTO[]>('/incubator/portfolio/readiness-levels/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  ---

  ### 4.4 TRL/CRL Management (Startup)
  **Endpoints for Startups to manage their own readiness levels and evidences:**

  #### Readiness Levels (CRUD `/startup/readiness-levels/`)
  - `GET /startup/readiness-levels/` - List all readiness levels for the startup.
  - `POST /startup/readiness-levels/` - Create a new readiness level.
  - `PUT/PATCH /startup/readiness-levels/{id}/` - Update a readiness level.
  - `DELETE /startup/readiness-levels/{id}/` - Delete a readiness level (and its evidences).

  **Response (List Readiness Levels)**
  ```json
  [
    {
      "id": 1,
      "startup": 3,
      "type": "TRL",
      "level": 1,
      "title": "Basic Principles Observed",
      "subtitle": "Scientific research begins...",
      "created": "2025-12-01T10:00:00Z",
      "updated": "2025-12-01T10:00:00Z"
    },
    {
      "id": 2,
      "startup": 3,
      "type": "TRL",
      "level": 2,
      "title": "Technology Concept Formulated",
      "subtitle": "Practical applications identified...",
      "created": "2025-12-01T10:00:00Z",
      "updated": "2025-12-01T10:00:00Z"
    }
  ]
  ```

  **Request (Create Readiness Level)**
  ```json
  {
    "type": "TRL",
    "level": 3,
    "title": "Proof of Concept",
    "subtitle": "Active R&D is initiated"
  }
  ```

  #### Evidences (CRUD `/startup/evidences/`)
  - `GET /startup/evidences/` - List all evidences for the startup.
  - `POST /startup/evidences/` - Create a new evidence.
  - `PUT/PATCH /startup/evidences/{id}/` - Update an evidence.
  - `DELETE /startup/evidences/{id}/` - Delete an evidence.

  **Response (List Evidences)**
  ```json
  [
    {
      "id": 10,
      "type": "TRL",
      "level": 3,
      "description": "Working prototype demonstrated",
      "file_url": "https://storage.googleapis.com/.../prototype-demo.mp4",
      "status": "PENDING",
      "reviewer_notes": null,
      "created": "2025-12-01T10:00:00Z",
      "updated": "2025-12-01T10:00:00Z"
    }
  ]
  ```

  **Request (Create Evidence)**
  ```json
  {
    "type": "TRL",
    "level": 3,
    "description": "Working prototype demonstrated to investors",
    "file_url": "https://storage.googleapis.com/.../prototype-demo.mp4"
  }
  ```

  **Response (Create Evidence)**
  ```json
  {
    "id": 11,
    "type": "TRL",
    "level": 3,
    "description": "Working prototype demonstrated to investors",
    "file_url": "https://storage.googleapis.com/.../prototype-demo.mp4",
    "status": "PENDING",
    "reviewer_notes": null,
    "created": "2025-12-04T09:00:00Z",
    "updated": "2025-12-04T09:00:00Z"
  }
  ```

  **Axios TS Interfaces**
  ```ts
  export interface ReadinessLevelDTO {
    id: number;
    startup: number;
    type: 'TRL' | 'CRL';
    level: number;
    title: string;
    subtitle?: string;
    created: string;
    updated: string;
  }

  export interface EvidenceDTO {
    id: number;
    type: 'TRL' | 'CRL';
    level: number;
    description?: string;
    file_url?: string;
    status: 'PENDING' | 'APPROVED' | 'REJECTED';
    reviewer_notes?: string;
    created: string;
    updated: string;
  }

  // Readiness Levels
  export const fetchReadinessLevels = async (token: string): Promise<ReadinessLevelDTO[]> => {
    const resp = await axios.get<ReadinessLevelDTO[]>('/startup/readiness-levels/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const createReadinessLevel = async (
    token: string, 
    data: Partial<ReadinessLevelDTO>
  ): Promise<ReadinessLevelDTO> => {
    const resp = await axios.post<ReadinessLevelDTO>('/startup/readiness-levels/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const deleteReadinessLevel = async (token: string, id: number): Promise<void> => {
    await axios.delete(`/startup/readiness-levels/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  };

  // Evidences
  export const fetchEvidences = async (token: string): Promise<EvidenceDTO[]> => {
    const resp = await axios.get<EvidenceDTO[]>('/startup/evidences/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const createEvidence = async (
    token: string, 
    data: Partial<EvidenceDTO>
  ): Promise<EvidenceDTO> => {
    const resp = await axios.post<EvidenceDTO>('/startup/evidences/', data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const updateEvidence = async (
    token: string, 
    id: number, 
    data: Partial<EvidenceDTO>
  ): Promise<EvidenceDTO> => {
    const resp = await axios.patch<EvidenceDTO>(`/startup/evidences/${id}/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };

  export const deleteEvidence = async (token: string, id: number): Promise<void> => {
    await axios.delete(`/startup/evidences/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  };
  ```

  ---

  ### 4.5 TRL/CRL Flow Summary

  **Startup Flow:**
  1. Startup creates `ReadinessLevel` entries for each TRL/CRL level they claim.
  2. Startup uploads `Evidence` for each level (documents, videos, etc.).
  3. Evidence starts with `status: PENDING`.

  **Incubator Flow:**
  1. Incubator views all evidences from portfolio via `/incubator/portfolio/evidences/`.
  2. Incubator reviews and approves/rejects via `POST /incubator/portfolio/evidences/{id}/review/`.
  3. On approval, if the evidence level is higher than current startup level, **auto-updates** `TRL_level` or `CRL_level`.

  **Status Values:**
  - `PENDING` - Awaiting review
  - `APPROVED` - Validated by incubator
  - `REJECTED` - Needs revision

  ---

  ### 4.6 Portfolio Campaigns (Incubator Dashboard)
  **Endpoint:** `GET /incubator/portfolio/campaigns/`
  **Description:** Returns all startups in the portfolio with their complete campaign data, financials, and investment rounds.

  **Response**
  ```json
  [
    {
      "startup_id": 3,
      "startup_name": "Acme Corp",
      "startup_logo": "https://storage.googleapis.com/.../logo.png",
      "industry": "Fintech",
      "trl_level": 5,
      "crl_level": 3,
      "campaign": {
        "id": 1,
        "status": "DRAFT",
        "problem": "Banks are slow...",
        "solution": "Digital payments...",
        "financials": {
          "id": 1,
          "funding_goal": "500000.00",
          "valuation": "2000000.00",
          "total_capital_injection": 150000.00,
          "current_cash_balance": "100000.00",
          "monthly_burn_rate": "25000.00",
          "financial_projections": {...}
        },
        "rounds": [
          {
            "id": 1,
            "name": "Pre-Seed",
            "target_amount": "200000.00",
            "total_committed_amount": 50000.00,
            "status": "OPEN",
            "investors": [
              {
                "id": 10,
                "incubator_id": 1,
                "incubator_details": {"id": 1, "name": "Y Combinator"},
                "status": "COMMITTED",
                "amount": "50000.00"
              }
            ]
          }
        ]
      }
    },
    {
      "startup_id": 5,
      "startup_name": "Beta Labs",
      "startup_logo": null,
      "industry": "HealthTech",
      "trl_level": 2,
      "crl_level": 1,
      "campaign": null
    }
  ]
  ```

  **Axios TS Interfaces**
  ```ts
  export interface PortfolioCampaignDTO {
    startup_id: number;
    startup_name: string;
    startup_logo?: string;
    industry?: string;
    trl_level: number;
    crl_level: number;
    campaign: CampaignDTO | null;
  }

  export const fetchPortfolioCampaigns = async (token: string): Promise<PortfolioCampaignDTO[]> => {
    const resp = await axios.get<PortfolioCampaignDTO[]>('/incubator/portfolio/campaigns/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return resp.data;
  };
  ```

  **Use Case:**
  - Dashboard de Incubadora para ver el estado financiero de todas las startups.
  - Calcular métricas agregadas del portafolio.
  - Ver rondas de inversión y capital comprometido por startup.

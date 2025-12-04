# Onboarding Wizard - Phase 2 Implementation

## Overview
This document describes the implementation of the complete Onboarding Wizard (Phase 2) for Raven CRM, which replaces mock data with real data from startups.

## Backend Changes

### 1. New Models (users/models.py)

Three new models have been added to support the onboarding wizard:

#### Evidence
Stores TRL/CRL evidence files and descriptions.
- **Fields**: `startup`, `trl_level`, `description`, `file`, `file_url`, `status`, `reviewer_notes`
- **Related Name**: `startup.evidences`
- **Indexes**: `startup + trl_level`, `status`

#### FinancialInput
Stores financial data for periods (usually monthly).
- **Fields**: `startup`, `period_date`, `revenue`, `costs`, `cash_balance`, `monthly_burn`, `notes`
- **Related Name**: `startup.financial_inputs`
- **Unique Constraint**: `startup + period_date`
- **Property**: `net_cash_flow` (calculated)

#### InvestorPipeline
Tracks investor relationships and fundraising pipeline.
- **Fields**: `startup`, `investor_name`, `investor_email`, `stage`, `ticket_size`, `notes`, `next_action_date`
- **Related Name**: `startup.investor_pipeline`
- **Choices**: 7 stages from `CONTACTED` to `COMMITTED`

### 2. New Serializers (users/serializers/onboarding.py)

#### Individual Serializers
- `EvidenceSerializer`: Handles evidence data with TRL validation
- `FinancialInputSerializer`: Handles financial data with numeric validations
- `InvestorPipelineSerializer`: Handles investor data

#### Main Serializer
- `OnboardingWizardSerializer`: Nested serializer that handles complete wizard submission
  - Validates all nested data
  - Implements `@transaction.atomic` for data integrity
  - Deletes all mock data before creating real data


### 3. New View (users/views.py)

#### OnboardingCompleteView
- **Endpoint**: `POST /api/users/startup/complete-onboarding/`
- **Authentication**: Required (IsAuthenticated)
- **User Type**: Startup only
- **Functionality**:
  1. Validates complete wizard payload
  2. Deletes all existing mock data
  3. Creates real data from wizard
  4. Updates startup status
  5. Comprehensive logging for auditing

### 4. New URL Route (users/urls.py)
```python
path('startup/complete-onboarding/', OnboardingCompleteView.as_view(), name='complete_onboarding')
```

## Database Migrations

After pulling these changes, run the following commands:

```bash
# Navigate to backend directory
cd backend/daddy-django

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Create migrations
python manage.py makemigrations

# Review migrations (optional but recommended)
python manage.py showmigrations

# Apply migrations
python manage.py migrate
```

## Django Admin Registration

Add the following to `users/admin.py`:

```python
from users.models import Evidence, FinancialInput, InvestorPipeline

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('startup', 'trl_level', 'status', 'created')
    list_filter = ('status', 'trl_level', 'created')
    search_fields = ('startup__company_name', 'description')
    readonly_fields = ('created', 'updated')

@admin.register(FinancialInput)
class FinancialInputAdmin(admin.ModelAdmin):
    list_display = ('startup', 'period_date', 'revenue', 'costs', 'cash_balance', 'monthly_burn')
    list_filter = ('period_date', 'created')
    search_fields = ('startup__company_name', 'notes')
    readonly_fields = ('created', 'updated')
    ordering = ('-period_date',)

@admin.register(InvestorPipeline)
class InvestorPipelineAdmin(admin.ModelAdmin):
    list_display = ('startup', 'investor_name', 'stage', 'ticket_size', 'created')
    list_filter = ('stage', 'created')
    search_fields = ('startup__company_name', 'investor_name', 'investor_email')
    readonly_fields = ('created', 'updated')
```

## Frontend Changes

### 1. New TypeScript Interfaces (src/types/onboarding.ts)
- `EvidenceData`, `EvidenceResponse`
- `FinancialData`, `FinancialDataResponse`
- `InvestorData`, `InvestorDataResponse`
- `OnboardingWizardPayload` (main payload structure)
- `OnboardingFormState` (React state management)

### 2. New Page Component (src/pages/startup/OnboardingWizard/)
- `OnboardingWizard.tsx`: Main wizard component with 3 steps
- `OnboardingWizard.css`: Complete styling following project patterns
- Features:
  - Step 1: TRL/CRL with evidence upload
  - Step 2: Financial data (3 key metrics)
  - Step 3: Investor pipeline with dynamic form
  - Progress bar with visual feedback
  - Form validation and error handling
  - Toast notifications

### 3. Translations (src/locales/common.tsx)
40+ new translation keys added for both Spanish and English:
- Wizard step labels
- Form field labels
- Validation messages
- Success/error messages

### 4. Routes (src/routes/routes.tsx)
```typescript
onboardingWizard: "/onboarding/wizard"
```

### 5. App Integration (src/App.tsx)
New protected route added with OnboardingRoute guard.

## API Payload Structure

The frontend sends the following structure to the backend:

```json
{
  "current_trl": 3,
  "target_funding_amount": 150000.00,
  "evidences": [
    {
      "trl_level": 3,
      "description": "Proof of concept completed with functional prototype",
      "file_url": "https://storage.example.com/evidence.pdf"
    }
  ],
  "financial_data": [
    {
      "period_date": "2024-01-31",
      "revenue": 5000.00,
      "costs": 8000.00,
      "cash_balance": 45000.00,
      "monthly_burn": 3000.00,
      "notes": "Initial revenue from beta customers"
    }
  ],
  "investors": [
    {
      "investor_name": "Angel Investor 1",
      "investor_email": "investor@example.com",
      "stage": "CONTACTED",
      "ticket_size": 50000.00,
      "notes": "Met at TechCrunch Disrupt"
    }
  ]
}
```

## Security Considerations

1. **Authentication**: Only authenticated startup users can access the endpoint
2. **User Type Validation**: Endpoint checks user type before processing
3. **Transaction Atomic**: All database operations are wrapped in a transaction
4. **Data Validation**: Comprehensive validation at serializer level
5. **Logging**: All operations are logged for audit trail

## Testing

### Backend Testing
```bash
# Test the endpoint with curl
curl -X POST http://localhost:8000/api/users/startup/complete-onboarding/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### Frontend Testing
1. Navigate to `/onboarding/wizard`
2. Complete all 3 steps with valid data
3. Submit the form
4. Verify redirect to dashboard


## Troubleshooting

### Common Issues

1. **Migration Conflicts**
   - Run: `python manage.py migrate --run-syncdb`
   - Or: `python manage.py migrate --fake-initial`

2. **Import Errors**
   - Ensure `users/serializers/onboarding.py` exists
   - Check `__init__.py` in serializers directory

3. **Frontend Build Errors**
   - Clear node_modules and reinstall: `npm ci`
   - Check TypeScript types match backend

4. **CORS Issues**
   - Verify `CORS_ALLOWED_ORIGINS` in Django settings
   - Check axios instance configuration

## Next Steps

1. Create migration files
2. Register models in Django admin
3. Test the complete flow end-to-end
4. Create mock data seeding script
5. Add unit tests for serializers
6. Add integration tests for the endpoint
7. Document the wizard flow in user documentation

## Questions or Issues?

Contact the development team or refer to:
- Django REST Framework docs: https://www.django-rest-framework.org/
- React Query docs: https://tanstack.com/query/latest
- Project-specific documentation in CLAUDE.md

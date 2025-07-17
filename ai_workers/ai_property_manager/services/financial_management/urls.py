"""
🏦 FINANCIAL MANAGEMENT URLS

URL routing for the comprehensive financial management system.
NOW WITH BUSINESS ISOLATION SUPPORT

Handles routing for:
- Business-isolated financial operations
- Payment tracking and balance management
- Automated payment reminders  
- Overdue payment detection
- Financial reporting
- Late fee management

Tasks covered:
- Task 24: Send rental payment reminders
- Task 25: Track rent payments & balances
- Task 26: Auto-generate financial reports
- Task 27: Detect overdue payments
- Task 28: Issue late fee notices
"""

from django.urls import path, include
from ai_workers.ai_property_manager.business_financial_api import (
    business_financial_api,
    deploy_property_manager
)

# Import original API for backwards compatibility
from .api import (
    financial_management_api,
    track_payment_api,
    send_reminders_api,
    overdue_payments_api,
    generate_report_api,
    apply_late_fees_api
)

app_name = 'financial_management'

urlpatterns = [
    # � BUSINESS-ISOLATED FINANCIAL MANAGEMENT API (NEW)
    path('business/', business_financial_api, name='business_financial_api'),
    path('business/deploy/', deploy_property_manager, name='deploy_property_manager'),
    
    # 🏦 LEGACY FINANCIAL MANAGEMENT API (for backwards compatibility)
    path('api/', financial_management_api, name='financial_management_api'),
    
    # 💰 PAYMENT TRACKING (Task 25)
    path('api/track-payment/', track_payment_api, name='track_payment_api'),
    path('api/payments/', financial_management_api, name='payments_api'),
    
    # 📢 PAYMENT REMINDERS (Task 24)
    path('api/send-reminders/', send_reminders_api, name='send_reminders_api'),
    path('api/reminders/', financial_management_api, name='reminders_api'),
    
    # 🚨 OVERDUE DETECTION (Task 27)
    path('api/overdue-payments/', overdue_payments_api, name='overdue_payments_api'),
    path('api/overdue/', financial_management_api, name='overdue_api'),
    
    # 📊 FINANCIAL REPORTS (Task 26)
    path('api/generate-report/', generate_report_api, name='generate_report_api'),
    path('api/reports/', financial_management_api, name='reports_api'),
    
    # ⚖️ LATE FEE MANAGEMENT (Task 28)
    path('api/apply-late-fees/', apply_late_fees_api, name='apply_late_fees_api'),
    path('api/late-fees/', financial_management_api, name='late_fees_api'),
    
    # 📈 DASHBOARD & ANALYTICS
    path('api/dashboard/', financial_management_api, name='dashboard_api'),
    path('api/tenant/<str:tenant_id>/', financial_management_api, name='tenant_details_api'),
]

# API Endpoint Documentation
"""
🔗 BUSINESS-ISOLATED FINANCIAL MANAGEMENT API ENDPOINTS

=== NEW BUSINESS API ENDPOINTS ===
POST /business/
GET  /business/

Business-isolated endpoint for all financial management operations.
Automatically filters data by authenticated user's business.

POST Request Format:
{
    "action": "track_payment|send_reminders|detect_overdue|generate_report|apply_late_fees|get_dashboard",
    "data": { ...action-specific data... }
}

GET Parameters:
- report_type: dashboard|properties|tenants|config

=== BUSINESS DEPLOYMENT ===
POST /business/deploy/
{
    "config": {
        "max_properties": 50,
        "financial_management_enabled": true,
        "payment_reminders_enabled": true,
        "auto_late_fees": true,
        "late_fee_amount": 75.00
    }
}

=== LEGACY API ENDPOINTS (for backwards compatibility) ===

💰 PAYMENT TRACKING:
POST /api/track-payment/
{
    "lease_id": "123",
    "amount": 1500.00,
    "payment_date": "2024-01-15",
    "payment_type": "rent"
}

📢 PAYMENT REMINDERS:
POST /api/send-reminders/
{} (no data required - sends all due reminders)

🚨 OVERDUE DETECTION:
GET /api/overdue-payments/
Returns all overdue payments with risk analysis

📊 REPORT GENERATION:
POST /api/generate-report/
{
    "report_type": "monthly_summary|payment_status|overdue_report|annual_summary",
    "year": 2024,
    "month": 1
}

⚖️ LATE FEE APPLICATION:
POST /api/apply-late-fees/
{
    "lease_id": "123",  // optional
    "force_apply": false
}

=== BUSINESS ISOLATION FEATURES ===

✅ Automatic Data Filtering:
- Each business only sees their own properties, tenants, and payments
- API automatically filters by authenticated user's business

✅ Permission Control:
- Only deployed AI Property Manager businesses can access endpoints
- Configurable feature toggles per business

✅ Usage Tracking:
- Track API usage per business for billing
- Monitor financial metrics per business

✅ Custom Configuration:
- Business-specific late fee rules
- Custom reminder schedules
- Branded email templates

=== AUTHENTICATION ===

All business endpoints require:
- User authentication (@login_required)
- Active business account
- Deployed AI Property Manager
- Active BusinessPropertyManagerConfig

=== ERROR HANDLING ===

- 403: Business not configured or AI Property Manager not deployed
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (authentication required)
- 500: Internal Server Error

All errors include descriptive error messages and business context.
"""

"""
🏦 FINANCIAL MANAGEMENT API

Unified API for comprehensive financial management services.

Endpoints:
- Payment tracking and balance management
- Automated payment reminders
- Overdue payment detection
- Financial reporting
- Late fee management

This brings together all financial management tasks:
- Task 24: Send rental payment reminders
- Task 25: Track rent payments & balances
- Task 26: Auto-generate financial reports
- Task 27: Detect overdue payments
- Task 28: Issue late fee notices
"""

import logging
import asyncio
from datetime import datetime, date
from typing import Dict, List, Optional
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from .payment_tracker import PaymentTracker
from .reminder_service import ReminderService
from .overdue_detector import OverdueDetector
from .report_generator import ReportGenerator
from .late_fee_manager import LateFeeManager

logger = logging.getLogger(__name__)


class FinancialManagementAPI(View):
    """
    🏦 FINANCIAL MANAGEMENT API: Unified financial operations
    
    Provides comprehensive financial management through a single API
    with intelligent automation and real-time analytics.
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def __init__(self):
        super().__init__()
        self.payment_tracker = PaymentTracker()
        self.reminder_service = ReminderService()
        self.overdue_detector = OverdueDetector()
        self.report_generator = ReportGenerator()
        self.late_fee_manager = LateFeeManager()
    
    def post(self, request):
        """
        Handle financial management operations
        
        POST data format:
        {
            "action": "track_payment|send_reminders|detect_overdue|generate_report|apply_late_fees",
            "data": { ... action-specific data ... }
        }
        """
        try:
            data = json.loads(request.body)
            action = data.get('action')
            action_data = data.get('data', {})
            
            # Route to appropriate service
            if action == 'track_payment':
                result = self._handle_track_payment(action_data)
            elif action == 'send_reminders':
                result = self._handle_send_reminders(action_data)
            elif action == 'detect_overdue':
                result = self._handle_detect_overdue(action_data)
            elif action == 'generate_report':
                result = self._handle_generate_report(action_data)
            elif action == 'apply_late_fees':
                result = self._handle_apply_late_fees(action_data)
            elif action == 'get_tenant_balance':
                result = self._handle_get_tenant_balance(action_data)
            elif action == 'get_all_balances':
                result = self._handle_get_all_balances(action_data)
            elif action == 'schedule_reminders':
                result = self._handle_schedule_reminders(action_data)
            elif action == 'waive_late_fee':
                result = self._handle_waive_late_fee(action_data)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown action: {action}',
                    'available_actions': [
                        'track_payment', 'send_reminders', 'detect_overdue',
                        'generate_report', 'apply_late_fees', 'get_tenant_balance',
                        'get_all_balances', 'schedule_reminders', 'waive_late_fee'
                    ]
                }, status=400)
            
            # Add metadata
            result['action'] = action
            result['timestamp'] = datetime.now().isoformat()
            result['service'] = 'Financial Management API'
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
            
        except Exception as e:
            logger.error(f"❌ Financial management API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Financial management operation failed: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """
        Get financial management status and analytics
        """
        try:
            # Get query parameters
            report_type = request.GET.get('report_type', 'dashboard')
            tenant_id = request.GET.get('tenant_id')
            
            if report_type == 'dashboard':
                result = self._get_financial_dashboard()
            elif report_type == 'tenant_details' and tenant_id:
                result = self._get_tenant_financial_details(tenant_id)
            elif report_type == 'overdue_summary':
                result = self.overdue_detector.detect_overdue_payments()
            elif report_type == 'late_fee_summary':
                result = self.late_fee_manager.get_late_fee_summary()
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid report type or missing parameters',
                    'available_reports': [
                        'dashboard', 'tenant_details', 'overdue_summary', 'late_fee_summary'
                    ]
                }, status=400)
            
            result['timestamp'] = datetime.now().isoformat()
            result['service'] = 'Financial Management API'
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"❌ Financial management GET error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Financial management query failed: {str(e)}'
            }, status=500)
    
    def _handle_track_payment(self, data: Dict) -> Dict:
        """Handle payment tracking"""
        required_fields = ['lease_id', 'amount']
        if not all(field in data for field in required_fields):
            return {
                'success': False,
                'error': f'Missing required fields: {required_fields}'
            }
        
        return self.payment_tracker.track_payment(
            lease_id=data['lease_id'],
            amount=data['amount'],
            payment_date=data.get('payment_date'),
            payment_type=data.get('payment_type', 'rent'),
            payment_method=data.get('payment_method'),
            transaction_id=data.get('transaction_id'),
            description=data.get('description'),
            notes=data.get('notes')
        )
    
    def _handle_send_reminders(self, data: Dict) -> Dict:
        """Handle sending payment reminders"""
        return self.reminder_service.send_due_reminders()
    
    def _handle_detect_overdue(self, data: Dict) -> Dict:
        """Handle overdue payment detection"""
        return self.overdue_detector.detect_overdue_payments()
    
    def _handle_generate_report(self, data: Dict) -> Dict:
        """Handle report generation"""
        report_type = data.get('report_type', 'monthly_summary')
        
        if report_type == 'monthly_summary':
            return self.report_generator.generate_monthly_summary(
                year=data.get('year'),
                month=data.get('month')
            )
        elif report_type == 'payment_status':
            return self.report_generator.generate_payment_status_report()
        elif report_type == 'overdue_report':
            return self.report_generator.generate_overdue_report(
                detailed=data.get('detailed', True)
            )
        elif report_type == 'annual_summary':
            return self.report_generator.generate_annual_summary(
                year=data.get('year')
            )
        else:
            return {
                'success': False,
                'error': f'Unknown report type: {report_type}',
                'available_types': ['monthly_summary', 'payment_status', 'overdue_report', 'annual_summary']
            }
    
    def _handle_apply_late_fees(self, data: Dict) -> Dict:
        """Handle late fee application"""
        return self.late_fee_manager.apply_late_fees(
            lease_id=data.get('lease_id'),
            force_apply=data.get('force_apply', False)
        )
    
    def _handle_get_tenant_balance(self, data: Dict) -> Dict:
        """Handle tenant balance inquiry"""
        tenant_id = data.get('tenant_id')
        if not tenant_id:
            return {
                'success': False,
                'error': 'tenant_id is required'
            }
        
        return self.payment_tracker.calculate_tenant_balance(tenant_id)
    
    def _handle_get_all_balances(self, data: Dict) -> Dict:
        """Handle all balances inquiry"""
        return self.payment_tracker.get_all_balances()
    
    def _handle_schedule_reminders(self, data: Dict) -> Dict:
        """Handle reminder scheduling"""
        return self.reminder_service.schedule_payment_reminders(
            lease_id=data.get('lease_id')
        )
    
    def _handle_waive_late_fee(self, data: Dict) -> Dict:
        """Handle late fee waiver"""
        required_fields = ['late_fee_id', 'reason']
        if not all(field in data for field in required_fields):
            return {
                'success': False,
                'error': f'Missing required fields: {required_fields}'
            }
        
        return self.late_fee_manager.waive_late_fee(
            late_fee_id=data['late_fee_id'],
            reason=data['reason'],
            waived_by=data.get('waived_by', 'AI System')
        )
    
    def _get_financial_dashboard(self) -> Dict:
        """Get comprehensive financial dashboard"""
        try:
            # Get all key financial metrics
            all_balances = self.payment_tracker.get_all_balances()
            overdue_analysis = self.overdue_detector.detect_overdue_payments()
            late_fee_summary = self.late_fee_manager.get_late_fee_summary(3)  # Last 3 months
            
            dashboard = {
                'success': True,
                'dashboard_type': 'financial_overview',
                'summary': {
                    'total_tenants': all_balances.get('total_tenants', 0),
                    'total_monthly_rent': all_balances.get('total_monthly_rent', 0),
                    'total_outstanding': all_balances.get('total_outstanding', 0),
                    'collection_rate': all_balances.get('collection_rate', 0),
                    'overdue_payments': overdue_analysis.get('total_overdue_payments', 0),
                    'overdue_amount': overdue_analysis.get('total_overdue_amount', 0),
                    'late_fees_this_quarter': late_fee_summary.get('total_amount', 0)
                },
                'tenant_status': {
                    'current': all_balances.get('current_tenants', 0),
                    'overdue': all_balances.get('overdue_tenants', 0)
                },
                'risk_analysis': overdue_analysis.get('risk_summary', {}),
                'urgent_actions': {
                    'escalation_required': len(overdue_analysis.get('escalation_required', [])),
                    'reminders_to_send': 0,  # Would calculate pending reminders
                    'late_fees_to_apply': 0  # Would calculate eligible late fees
                },
                'recent_activity': {
                    'last_payment': None,  # Would get latest payment
                    'recent_late_fees': late_fee_summary.get('total_late_fees', 0),
                    'recent_waivers': late_fee_summary.get('waived_fees', 0)
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Dashboard generation failed: {str(e)}")
            return {
                'success': False,
                'error': f'Dashboard generation failed: {str(e)}'
            }
    
    def _get_tenant_financial_details(self, tenant_id: str) -> Dict:
        """Get detailed financial information for a specific tenant"""
        try:
            balance_info = self.payment_tracker.calculate_tenant_balance(tenant_id)
            payment_history = self.payment_tracker.get_payment_history(tenant_id, 12)
            risk_profile = self.overdue_detector.get_tenant_risk_profile(tenant_id)
            
            return {
                'success': True,
                'tenant_id': tenant_id,
                'balance_info': balance_info,
                'payment_history': payment_history,
                'risk_profile': risk_profile,
                'detailed_view': True
            }
            
        except Exception as e:
            logger.error(f"❌ Tenant details retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': f'Tenant details retrieval failed: {str(e)}'
            }


# Convenience function views for easy URL routing
@csrf_exempt
@require_http_methods(["POST", "GET"])
def financial_management_api(request):
    """
    🏦 MAIN FINANCIAL MANAGEMENT API
    
    Unified endpoint for all financial management operations
    """
    view = FinancialManagementAPI()
    return view.dispatch(request)


@csrf_exempt
@require_http_methods(["POST"])
def track_payment_api(request):
    """💰 TRACK PAYMENT: Quick payment tracking endpoint"""
    try:
        data = json.loads(request.body)
        tracker = PaymentTracker()
        result = tracker.track_payment(**data)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_reminders_api(request):
    """📢 SEND REMINDERS: Quick reminder sending endpoint"""
    try:
        reminder_service = ReminderService()
        result = reminder_service.send_due_reminders()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def overdue_payments_api(request):
    """🚨 OVERDUE PAYMENTS: Quick overdue detection endpoint"""
    try:
        detector = OverdueDetector()
        result = detector.detect_overdue_payments()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_report_api(request):
    """📊 GENERATE REPORT: Quick report generation endpoint"""
    try:
        data = json.loads(request.body)
        generator = ReportGenerator()
        
        report_type = data.get('report_type', 'monthly_summary')
        if report_type == 'monthly_summary':
            result = generator.generate_monthly_summary(
                year=data.get('year'),
                month=data.get('month')
            )
        elif report_type == 'payment_status':
            result = generator.generate_payment_status_report()
        else:
            result = {
                'success': False,
                'error': f'Unsupported report type: {report_type}'
            }
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def apply_late_fees_api(request):
    """⚖️ APPLY LATE FEES: Quick late fee application endpoint"""
    try:
        data = json.loads(request.body)
        late_fee_manager = LateFeeManager()
        result = late_fee_manager.apply_late_fees(
            lease_id=data.get('lease_id'),
            force_apply=data.get('force_apply', False)
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

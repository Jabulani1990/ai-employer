"""
🏢 BUSINESS-AWARE FINANCIAL MANAGEMENT API

This provides business-isolated access to financial management services.
Each business can only access their own data.
"""

import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json

from business.models import Business, AIEmployer, BusinessAIWorker
from ai_workers.ai_property_manager.business_integration import BusinessPropertyManagerConfig
from ai_workers.ai_property_manager.services.financial_management import (
    PaymentTracker,
    ReminderService,
    OverdueDetector,
    ReportGenerator,
    LateFeeManager
)

logger = logging.getLogger(__name__)


class BusinessFinancialAPI(View):
    """
    🏦 BUSINESS-ISOLATED FINANCIAL MANAGEMENT API
    
    Provides financial management services with proper business isolation.
    Each business can only access their own data.
    """
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_business_context(self, request):
        """Get business context for the authenticated user"""
        try:
            # Get the business for the authenticated user
            business = Business.objects.get(owner=request.user)
            ai_employer = AIEmployer.objects.get(business=business)
            
            # Check if they have Property Manager deployed
            try:
                property_manager = BusinessAIWorker.objects.get(
                    business=request.user,
                    ai_employer=ai_employer,
                    ai_worker__name="AI Property Manager",
                    status="active"
                )
                
                config = BusinessPropertyManagerConfig.objects.get(
                    business=business,
                    ai_employer=ai_employer,
                    is_active=True
                )
                
                return {
                    'business': business,
                    'ai_employer': ai_employer,
                    'property_manager': property_manager,
                    'config': config,
                    'has_access': True
                }
                
            except (BusinessAIWorker.DoesNotExist, BusinessPropertyManagerConfig.DoesNotExist):
                return {
                    'business': business,
                    'has_access': False,
                    'error': 'AI Property Manager not deployed or configured'
                }
                
        except (Business.DoesNotExist, AIEmployer.DoesNotExist):
            return {
                'has_access': False,
                'error': 'Business not found or not properly configured'
            }
    
    def post(self, request):
        """Handle business-isolated financial operations"""
        try:
            # Get business context
            context = self.get_business_context(request)
            if not context['has_access']:
                return JsonResponse({
                    'success': False,
                    'error': context['error']
                }, status=403)
            
            # Parse request data
            data = json.loads(request.body)
            action = data.get('action')
            action_data = data.get('data', {})
            
            # Initialize services with business isolation
            business_id = str(context['business'].id)
            ai_employer_id = str(context['ai_employer'].id)
            
            payment_tracker = PaymentTracker(business_id=business_id, ai_employer_id=ai_employer_id)
            reminder_service = ReminderService(business_id=business_id, ai_employer_id=ai_employer_id)
            overdue_detector = OverdueDetector(business_id=business_id, ai_employer_id=ai_employer_id)
            report_generator = ReportGenerator(business_id=business_id, ai_employer_id=ai_employer_id)
            late_fee_manager = LateFeeManager(business_id=business_id, ai_employer_id=ai_employer_id)
            
            # Route to appropriate service
            if action == 'track_payment':
                result = payment_tracker.track_payment(**action_data)
            elif action == 'send_reminders':
                result = reminder_service.send_due_reminders()
            elif action == 'detect_overdue':
                result = overdue_detector.detect_overdue_payments()
            elif action == 'generate_report':
                result = report_generator.generate_monthly_summary(**action_data)
            elif action == 'apply_late_fees':
                result = late_fee_manager.apply_late_fees(**action_data)
            elif action == 'get_dashboard':
                result = self._get_business_dashboard(context)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown action: {action}'
                }, status=400)
            
            # Add business context to response
            result['business_name'] = context['business'].name
            result['action'] = action
            result['timestamp'] = datetime.now().isoformat()
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
            
        except Exception as e:
            logger.error(f"❌ Business Financial API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Financial operation failed: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """Get business financial dashboard and reports"""
        try:
            context = self.get_business_context(request)
            if not context['has_access']:
                return JsonResponse({
                    'success': False,
                    'error': context['error']
                }, status=403)
            
            report_type = request.GET.get('report_type', 'dashboard')
            
            if report_type == 'dashboard':
                result = self._get_business_dashboard(context)
            elif report_type == 'properties':
                result = self._get_business_properties(context)
            elif report_type == 'tenants':
                result = self._get_business_tenants(context)
            elif report_type == 'config':
                result = self._get_business_config(context)
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown report type: {report_type}'
                }, status=400)
            
            result['business_name'] = context['business'].name
            result['timestamp'] = datetime.now().isoformat()
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"❌ Business Financial GET error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Financial query failed: {str(e)}'
            }, status=500)
    
    def _get_business_dashboard(self, context):
        """Get comprehensive business dashboard"""
        business = context['business']
        config = context['config']
        
        # Get counts
        property_count = business.properties.count()
        tenant_count = business.tenants.count()
        active_leases = business.properties.filter(leases__status='active').count()
        
        # Get recent activity (you'll need to implement these queries)
        # recent_payments = Payment.objects.filter(lease__tenant__business=business).order_by('-created_at')[:5]
        
        return {
            'success': True,
            'dashboard_type': 'business_overview',
            'summary': {
                'total_properties': property_count,
                'total_tenants': tenant_count,
                'active_leases': active_leases,
                'max_properties': config.max_properties,
                'max_tenants': config.max_tenants,
                'can_add_property': config.can_add_property,
                'can_add_tenant': config.can_add_tenant,
            },
            'config': {
                'financial_management_enabled': config.financial_management_enabled,
                'payment_reminders_enabled': config.payment_reminders_enabled,
                'auto_late_fees': config.auto_late_fees,
                'late_fee_amount': float(config.late_fee_amount),
                'late_fee_grace_days': config.late_fee_grace_days,
            }
        }
    
    def _get_business_properties(self, context):
        """Get business properties list"""
        business = context['business']
        properties = business.properties.all().values(
            'id', 'title', 'property_type', 'status', 'price', 'location'
        )
        
        return {
            'success': True,
            'properties': list(properties),
            'total_count': len(properties)
        }
    
    def _get_business_tenants(self, context):
        """Get business tenants list"""
        business = context['business']
        tenants = business.tenants.all().values(
            'id', 'first_name', 'last_name', 'email', 'phone', 'is_active'
        )
        
        return {
            'success': True,
            'tenants': list(tenants),
            'total_count': len(tenants)
        }
    
    def _get_business_config(self, context):
        """Get business configuration"""
        config = context['config']
        
        return {
            'success': True,
            'config': {
                'max_properties': config.max_properties,
                'max_tenants': config.max_tenants,
                'financial_management_enabled': config.financial_management_enabled,
                'payment_reminders_enabled': config.payment_reminders_enabled,
                'auto_late_fees': config.auto_late_fees,
                'late_fee_amount': float(config.late_fee_amount),
                'late_fee_grace_days': config.late_fee_grace_days,
                'reminder_days_advance': config.reminder_days_advance,
                'auto_monthly_reports': config.auto_monthly_reports,
                'payment_processor': config.payment_processor,
            }
        }


# Convenience function views
@csrf_exempt
@login_required
@require_http_methods(["POST", "GET"])
def business_financial_api(request):
    """Main business financial API endpoint"""
    view = BusinessFinancialAPI()
    return view.dispatch(request)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def deploy_property_manager(request):
    """Deploy AI Property Manager for a business"""
    try:
        data = json.loads(request.body)
        
        # Get business
        business = Business.objects.get(owner=request.user)
        ai_employer = AIEmployer.objects.get(business=business)
        
        # Check if already deployed
        existing = BusinessAIWorker.objects.filter(
            business=request.user,
            ai_employer=ai_employer,
            ai_worker__name="AI Property Manager"
        ).exists()
        
        if existing:
            return JsonResponse({
                'success': False,
                'error': 'AI Property Manager already deployed'
            })
        
        # Get AI Worker template
        from ai_workers.models import AIWorker
        property_manager_template = AIWorker.objects.get(name="AI Property Manager")
        
        # Create business AI worker instance
        business_ai_worker = BusinessAIWorker.objects.create(
            business=request.user,
            ai_employer=ai_employer,
            ai_worker=property_manager_template,
            configurations=data.get('config', {}),
            status='active'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'AI Property Manager deployed successfully',
            'deployment_id': str(business_ai_worker.id)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Deployment failed: {str(e)}'
        }, status=500)

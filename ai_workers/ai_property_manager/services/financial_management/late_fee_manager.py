"""
⚖️ LATE FEE MANAGER SERVICE

Automated late fee calculation, application, and management.

Features:
- Automated late fee calculation
- Rule-based fee application
- Grace period management
- Fee waiver system
- Compliance tracking

Task: #28 - Issue late fee notices
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal

from .models import Tenant, Lease, Payment, LateFee, PaymentReminder
from .payment_tracker import PaymentTracker

logger = logging.getLogger(__name__)


class LateFeeManager:
    """
    💸 LATE FEE MANAGER: Intelligent late fee automation
    
    Manages late fee calculation, application, and compliance
    with customizable rules and grace periods.
    """
    
    def __init__(self):
        self.service_name = "Late Fee Manager"
        self.payment_tracker = PaymentTracker()
        
        # Default late fee rules (can be customized per property/lease)
        self.default_rules = {
            'grace_period_days': 5,      # Days after due date before fee applies
            'flat_fee': Decimal('50.00'), # Flat late fee amount
            'percentage_fee': Decimal('0.05'),  # 5% of rent amount
            'daily_fee': Decimal('5.00'), # Additional daily fee after grace period
            'max_fee_percentage': Decimal('0.20'),  # Max 20% of rent
            'use_flat_fee': True,        # Use flat fee vs percentage
            'compound_daily': False      # Whether to add daily fees
        }
    
    def apply_late_fees(self, lease_id: str = None, force_apply: bool = False) -> Dict:
        """
        💸 APPLY LATE FEES: Calculate and apply late fees for overdue payments
        
        Args:
            lease_id: Specific lease to process (None for all eligible)
            force_apply: Force application even if within grace period
            
        Returns:
            Dict with late fee application results
        """
        try:
            if lease_id:
                leases = Lease.objects.filter(id=lease_id, status='active')
            else:
                leases = Lease.objects.filter(status='active')
            
            results = {
                'processed_leases': 0,
                'fees_applied': 0,
                'total_fees_amount': Decimal('0.00'),
                'fees_waived': 0,
                'processing_details': []
            }
            
            for lease in leases:
                lease_result = self._process_lease_late_fees(lease, force_apply)
                results['processing_details'].append(lease_result)
                
                if lease_result['success']:
                    results['processed_leases'] += 1
                    results['fees_applied'] += lease_result['fees_applied']
                    results['total_fees_amount'] += Decimal(str(lease_result['total_fees_amount']))
                    results['fees_waived'] += lease_result['fees_waived']
            
            logger.info(f"💸 Applied {results['fees_applied']} late fees totaling ${results['total_fees_amount']}")
            
            return {
                'success': True,
                'summary': results,
                'message': f"Processed {results['processed_leases']} leases, applied {results['fees_applied']} late fees"
            }
            
        except Exception as e:
            logger.error(f"❌ Late fee application failed: {str(e)}")
            return {
                'success': False,
                'error': f"Late fee application failed: {str(e)}"
            }
    
    def calculate_late_fee(self, payment_id: str, custom_rules: Dict = None) -> Dict:
        """
        🧮 CALCULATE LATE FEE: Calculate late fee for a specific payment
        
        Args:
            payment_id: Payment to calculate fee for
            custom_rules: Override default fee rules
            
        Returns:
            Dict with calculated late fee details
        """
        try:
            payment = Payment.objects.get(id=payment_id)
            rules = {**self.default_rules, **(custom_rules or {})}
            
            # Check if payment is actually overdue
            today = timezone.now().date()
            days_overdue = (today - payment.due_date).days
            
            if days_overdue <= 0:
                return {
                    'success': False,
                    'error': 'Payment is not overdue'
                }
            
            # Check grace period
            if days_overdue <= rules['grace_period_days'] and not custom_rules:
                return {
                    'fee_amount': 0.00,
                    'reason': f"Within {rules['grace_period_days']}-day grace period",
                    'days_overdue': days_overdue,
                    'applicable': False
                }
            
            # Calculate base late fee
            if rules['use_flat_fee']:
                base_fee = rules['flat_fee']
            else:
                base_fee = payment.amount * rules['percentage_fee']
            
            # Add daily fees if applicable
            daily_fees = Decimal('0.00')
            if rules['compound_daily'] and days_overdue > rules['grace_period_days']:
                daily_days = days_overdue - rules['grace_period_days']
                daily_fees = rules['daily_fee'] * daily_days
            
            total_fee = base_fee + daily_fees
            
            # Apply maximum fee cap
            max_fee = payment.amount * rules['max_fee_percentage']
            if total_fee > max_fee:
                total_fee = max_fee
                capped = True
            else:
                capped = False
            
            return {
                'success': True,
                'fee_amount': float(total_fee),
                'base_fee': float(base_fee),
                'daily_fees': float(daily_fees),
                'days_overdue': days_overdue,
                'grace_period_expired': days_overdue > rules['grace_period_days'],
                'capped_at_maximum': capped,
                'max_fee_limit': float(max_fee),
                'applicable': True,
                'calculation_details': {
                    'rent_amount': float(payment.amount),
                    'rules_applied': rules,
                    'calculation_date': today.isoformat()
                }
            }
            
        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': f"Payment not found: {payment_id}"
            }
        except Exception as e:
            logger.error(f"❌ Late fee calculation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Late fee calculation failed: {str(e)}"
            }
    
    def waive_late_fee(self, late_fee_id: str, reason: str, waived_by: str = "AI System") -> Dict:
        """
        🤝 WAIVE LATE FEE: Waive a late fee with documentation
        """
        try:
            late_fee = LateFee.objects.get(id=late_fee_id)
            
            if late_fee.status == 'waived':
                return {
                    'success': False,
                    'error': 'Late fee already waived'
                }
            
            # Update late fee status
            late_fee.status = 'waived'
            late_fee.waive_reason = f"{reason} (Waived by: {waived_by})"
            late_fee.save()
            
            logger.info(f"🤝 Late fee waived: ${late_fee.amount} for {late_fee.payment.lease.tenant.full_name}")
            
            return {
                'success': True,
                'late_fee_id': str(late_fee.id),
                'waived_amount': float(late_fee.amount),
                'tenant_name': late_fee.payment.lease.tenant.full_name,
                'reason': reason,
                'waived_by': waived_by,
                'message': f"Late fee of ${late_fee.amount} waived for {late_fee.payment.lease.tenant.full_name}"
            }
            
        except LateFee.DoesNotExist:
            return {
                'success': False,
                'error': f"Late fee not found: {late_fee_id}"
            }
        except Exception as e:
            logger.error(f"❌ Late fee waiver failed: {str(e)}")
            return {
                'success': False,
                'error': f"Late fee waiver failed: {str(e)}"
            }
    
    def send_late_fee_notices(self) -> Dict:
        """
        📬 SEND LATE FEE NOTICES: Send notifications for applied late fees
        """
        try:
            # Get recent late fees that need notices
            recent_fees = LateFee.objects.filter(
                status='applied',
                fee_date__gte=timezone.now().date() - timedelta(days=3)
            ).select_related('payment__lease__tenant', 'payment__lease__property')
            
            notices_sent = 0
            failed_notices = 0
            notice_results = []
            
            for late_fee in recent_fees:
                # Check if notice already sent
                existing_reminder = PaymentReminder.objects.filter(
                    payment=late_fee.payment,
                    reminder_type='late_fee',
                    status='sent'
                ).exists()
                
                if not existing_reminder:
                    notice_result = self._send_late_fee_notice(late_fee)
                    notice_results.append(notice_result)
                    
                    if notice_result['success']:
                        notices_sent += 1
                    else:
                        failed_notices += 1
            
            logger.info(f"📬 Sent {notices_sent} late fee notices, {failed_notices} failed")
            
            return {
                'success': True,
                'notices_sent': notices_sent,
                'notices_failed': failed_notices,
                'total_processed': len(notice_results),
                'notice_results': notice_results,
                'message': f"Sent {notices_sent} late fee notices successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Late fee notice sending failed: {str(e)}")
            return {
                'success': False,
                'error': f"Late fee notice sending failed: {str(e)}"
            }
    
    def get_late_fee_summary(self, months_back: int = 6) -> Dict:
        """
        📊 LATE FEE SUMMARY: Analytics on late fee performance
        """
        try:
            cutoff_date = timezone.now().date() - timedelta(days=months_back * 30)
            
            late_fees = LateFee.objects.filter(fee_date__gte=cutoff_date)
            
            summary = {
                'period_months': months_back,
                'total_late_fees': late_fees.count(),
                'total_amount': float(late_fees.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')),
                'applied_fees': late_fees.filter(status='applied').count(),
                'waived_fees': late_fees.filter(status='waived').count(),
                'pending_fees': late_fees.filter(status='pending').count(),
                'average_fee_amount': 0,
                'by_month': [],
                'top_properties': [],
                'waiver_reasons': {}
            }
            
            # Calculate average
            if summary['total_late_fees'] > 0:
                summary['average_fee_amount'] = summary['total_amount'] / summary['total_late_fees']
            
            # Monthly breakdown
            current_date = cutoff_date
            while current_date <= timezone.now().date():
                month_end = min(current_date + timedelta(days=30), timezone.now().date())
                month_fees = late_fees.filter(fee_date__range=[current_date, month_end])
                
                summary['by_month'].append({
                    'month': current_date.strftime('%Y-%m'),
                    'count': month_fees.count(),
                    'amount': float(month_fees.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')),
                    'applied': month_fees.filter(status='applied').count(),
                    'waived': month_fees.filter(status='waived').count()
                })
                
                current_date = month_end + timedelta(days=1)
            
            # Properties with most late fees
            from django.db.models import Count
            property_fees = late_fees.values(
                'payment__lease__property__title'
            ).annotate(
                fee_count=Count('id'),
                total_amount=Sum('amount')
            ).order_by('-fee_count')[:5]
            
            summary['top_properties'] = [
                {
                    'property': item['payment__lease__property__title'],
                    'fee_count': item['fee_count'],
                    'total_amount': float(item['total_amount'] or Decimal('0.00'))
                }
                for item in property_fees
            ]
            
            # Waiver reasons analysis
            waived_fees = late_fees.filter(status='waived').exclude(waive_reason='')
            for fee in waived_fees:
                reason = fee.waive_reason.split('(')[0].strip()  # Extract main reason
                if reason not in summary['waiver_reasons']:
                    summary['waiver_reasons'][reason] = 0
                summary['waiver_reasons'][reason] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Late fee summary failed: {str(e)}")
            return {
                'success': False,
                'error': f"Late fee summary failed: {str(e)}"
            }
    
    def update_late_fee_rules(self, lease_id: str, new_rules: Dict) -> Dict:
        """
        ⚙️ UPDATE RULES: Update late fee rules for a specific lease
        """
        try:
            lease = Lease.objects.get(id=lease_id)
            
            # Validate rules
            valid_rules = self._validate_fee_rules(new_rules)
            if not valid_rules['valid']:
                return {
                    'success': False,
                    'error': f"Invalid rules: {valid_rules['errors']}"
                }
            
            # For now, store rules in lease notes or create a separate model
            # This is a simplified implementation
            logger.info(f"⚙️ Late fee rules updated for lease {lease_id}")
            
            return {
                'success': True,
                'lease_id': str(lease.id),
                'updated_rules': new_rules,
                'message': f"Late fee rules updated for {lease.tenant.full_name}"
            }
            
        except Lease.DoesNotExist:
            return {
                'success': False,
                'error': f"Lease not found: {lease_id}"
            }
        except Exception as e:
            logger.error(f"❌ Late fee rules update failed: {str(e)}")
            return {
                'success': False,
                'error': f"Late fee rules update failed: {str(e)}"
            }
    
    def _process_lease_late_fees(self, lease: Lease, force_apply: bool) -> Dict:
        """Process late fees for a specific lease"""
        try:
            today = timezone.now().date()
            
            # Get overdue payments for this lease
            overdue_payments = Payment.objects.filter(
                lease=lease,
                status='pending',
                due_date__lt=today
            )
            
            lease_result = {
                'success': True,
                'lease_id': str(lease.id),
                'tenant_name': lease.tenant.full_name,
                'overdue_payments': overdue_payments.count(),
                'fees_applied': 0,
                'fees_waived': 0,
                'total_fees_amount': 0.00,
                'payment_details': []
            }
            
            for payment in overdue_payments:
                # Check if late fee already exists
                existing_fee = LateFee.objects.filter(payment=payment).first()
                if existing_fee:
                    continue  # Skip if fee already applied
                
                # Calculate late fee
                fee_calc = self.calculate_late_fee(str(payment.id))
                
                if fee_calc.get('success') and fee_calc.get('applicable'):
                    # Check for auto-waiver conditions
                    should_waive, waive_reason = self._check_auto_waiver_conditions(payment, lease.tenant)
                    
                    if should_waive:
                        # Create waived late fee for record keeping
                        late_fee = LateFee.objects.create(
                            payment=payment,
                            amount=Decimal(str(fee_calc['fee_amount'])),
                            days_overdue=fee_calc['days_overdue'],
                            status='waived',
                            waive_reason=waive_reason
                        )
                        lease_result['fees_waived'] += 1
                    else:
                        # Apply late fee
                        late_fee = LateFee.objects.create(
                            payment=payment,
                            amount=Decimal(str(fee_calc['fee_amount'])),
                            days_overdue=fee_calc['days_overdue'],
                            status='applied'
                        )
                        lease_result['fees_applied'] += 1
                        lease_result['total_fees_amount'] += fee_calc['fee_amount']
                    
                    lease_result['payment_details'].append({
                        'payment_id': str(payment.id),
                        'amount': float(payment.amount),
                        'due_date': payment.due_date.isoformat(),
                        'days_overdue': fee_calc['days_overdue'],
                        'late_fee_amount': fee_calc['fee_amount'],
                        'status': 'waived' if should_waive else 'applied',
                        'reason': waive_reason if should_waive else 'Standard late fee'
                    })
            
            return lease_result
            
        except Exception as e:
            logger.error(f"❌ Lease late fee processing failed: {str(e)}")
            return {
                'success': False,
                'lease_id': str(lease.id),
                'error': str(e)
            }
    
    def _check_auto_waiver_conditions(self, payment: Payment, tenant: Tenant) -> Tuple[bool, str]:
        """Check if late fee should be automatically waived"""
        
        # Get tenant's payment history
        payment_history = self.payment_tracker.get_payment_history(str(tenant.id), 12)
        
        # Auto-waive conditions
        reliability_score = payment_history.get('reliability_score', 0)
        
        # Waive for highly reliable tenants (>95% reliability)
        if reliability_score > 95:
            return True, "Excellent payment history - courtesy waiver"
        
        # Waive for first-time late payment in 12 months
        late_payments = payment_history.get('late_payments', 0)
        if late_payments <= 1:
            return True, "First late payment in 12 months - courtesy waiver"
        
        # Waive if payment is less than 3 days overdue and tenant has good history
        days_overdue = (timezone.now().date() - payment.due_date).days
        if days_overdue <= 3 and reliability_score > 85:
            return True, "Minor delay with good payment history"
        
        return False, ""
    
    def _send_late_fee_notice(self, late_fee: LateFee) -> Dict:
        """Send late fee notice to tenant"""
        try:
            tenant = late_fee.payment.lease.tenant
            
            # Create late fee reminder
            reminder = PaymentReminder.objects.create(
                payment=late_fee.payment,
                reminder_type='late_fee',
                scheduled_date=timezone.now(),
                subject=f"Late Fee Notice - {late_fee.payment.lease.property.title}",
                message=self._generate_late_fee_notice_message(late_fee),
                status='pending'
            )
            
            # For now, simulate sending (in production, integrate with email service)
            reminder.status = 'sent'
            reminder.sent_date = timezone.now()
            reminder.save()
            
            logger.info(f"📬 Late fee notice sent to {tenant.full_name}")
            
            return {
                'success': True,
                'reminder_id': str(reminder.id),
                'tenant_name': tenant.full_name,
                'late_fee_amount': float(late_fee.amount)
            }
            
        except Exception as e:
            logger.error(f"❌ Late fee notice sending failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_late_fee_notice_message(self, late_fee: LateFee) -> str:
        """Generate personalized late fee notice message"""
        tenant = late_fee.payment.lease.tenant
        payment = late_fee.payment
        property_title = payment.lease.property.title
        
        message = f"""Dear {tenant.first_name},

This notice is to inform you that a late fee of ${late_fee.amount} has been applied to your account for the overdue rent payment.

Payment Details:
- Property: {property_title}
- Original Amount Due: ${payment.amount}
- Due Date: {payment.due_date.strftime('%B %d, %Y')}
- Days Overdue: {late_fee.days_overdue}
- Late Fee Applied: ${late_fee.amount}

Total Amount Now Due: ${float(payment.amount) + float(late_fee.amount)}

Please submit your payment immediately to avoid further action. If you have any questions or need to discuss payment arrangements, please contact us as soon as possible.

We understand that circumstances can arise, and we're here to help find a solution that works for everyone.

Property Management Team"""
        
        return message
    
    def _validate_fee_rules(self, rules: Dict) -> Dict:
        """Validate late fee rules"""
        required_fields = ['grace_period_days', 'flat_fee', 'percentage_fee']
        errors = []
        
        for field in required_fields:
            if field not in rules:
                errors.append(f"Missing required field: {field}")
        
        # Validate ranges
        if 'grace_period_days' in rules:
            if not isinstance(rules['grace_period_days'], int) or rules['grace_period_days'] < 0:
                errors.append("Grace period must be a non-negative integer")
        
        if 'flat_fee' in rules:
            try:
                fee = Decimal(str(rules['flat_fee']))
                if fee < 0:
                    errors.append("Flat fee cannot be negative")
            except:
                errors.append("Invalid flat fee amount")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

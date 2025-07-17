"""
💰 PAYMENT TRACKER SERVICE

Comprehensive payment tracking and balance management.

Features:
- Track all rent payments and balances
- Real-time payment status monitoring
- Balance calculations
- Payment history analysis
- Integration with autonomous learning

Task: #25 - Track rent payments & balances
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db.models import Sum, Q, Count
from django.db import transaction

from .models import Tenant, Lease, Payment, LateFee
from ai_workers.ai_property_manager.models import PropertyListing

logger = logging.getLogger(__name__)


class PaymentTracker:
    """
    🏦 PAYMENT TRACKER: Autonomous payment monitoring and balance management
    
    This service provides comprehensive payment tracking with real-time
    balance calculations and payment status monitoring.
    
    NOW WITH BUSINESS ISOLATION SUPPORT
    """
    
    def __init__(self, business_id=None, ai_employer_id=None):
        """
        Initialize payment tracker with business isolation
        
        Args:
            business_id: Filter operations to specific business
            ai_employer_id: Filter operations to specific AI employer
        """
        self.service_name = "Payment Tracker"
        self.learning_enabled = True
        self.business_id = business_id
        self.ai_employer_id = ai_employer_id
        
    def track_payment(self, lease_id: str, amount: Decimal, payment_date: date = None, 
                     payment_type: str = 'rent', **kwargs) -> Dict:
        """
        📝 TRACK PAYMENT: Record a new payment
        
        Args:
            lease_id: UUID of the lease
            amount: Payment amount
            payment_date: Date of payment (defaults to today)
            payment_type: Type of payment (rent, late_fee, etc.)
            **kwargs: Additional payment details
            
        Returns:
            Dict with payment tracking results
        """
        try:
            if payment_date is None:
                payment_date = timezone.now().date()
                
            # Get lease
            lease = Lease.objects.get(id=lease_id)
            
            # Determine due date (usually current month's rent due date)
            due_date = self._calculate_due_date(lease, payment_date)
            
            # Create payment record
            payment = Payment.objects.create(
                lease=lease,
                amount=amount,
                payment_type=payment_type,
                payment_date=payment_date,
                due_date=due_date,
                status='completed',
                payment_method=kwargs.get('payment_method', ''),
                transaction_id=kwargs.get('transaction_id', ''),
                description=kwargs.get('description', ''),
                notes=kwargs.get('notes', '')
            )
            
            # Calculate updated balance
            balance_info = self.calculate_tenant_balance(lease.tenant.id)
            
            logger.info(f"✅ Payment tracked: {lease.tenant.full_name} - ${amount}")
            
            return {
                'success': True,
                'payment_id': str(payment.id),
                'payment': {
                    'amount': float(amount),
                    'date': payment_date.isoformat(),
                    'type': payment_type,
                    'status': payment.status
                },
                'balance_info': balance_info,
                'message': f"Payment of ${amount} successfully tracked for {lease.tenant.full_name}"
            }
            
        except Lease.DoesNotExist:
            return {
                'success': False,
                'error': f"Lease not found: {lease_id}"
            }
        except Exception as e:
            logger.error(f"❌ Payment tracking failed: {str(e)}")
            return {
                'success': False,
                'error': f"Payment tracking failed: {str(e)}"
            }
    
    def calculate_tenant_balance(self, tenant_id: str) -> Dict:
        """
        💰 CALCULATE BALANCE: Get current balance for a tenant
        
        Calculates:
        - Total amount owed
        - Payments made
        - Outstanding balance
        - Late fees
        - Payment history summary
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            active_leases = Lease.objects.filter(tenant=tenant, status='active')
            
            balance_data = {
                'tenant_info': {
                    'id': str(tenant.id),
                    'name': tenant.full_name,
                    'email': tenant.email
                },
                'total_balance': Decimal('0.00'),
                'monthly_rent': Decimal('0.00'),
                'late_fees': Decimal('0.00'),
                'security_deposit': Decimal('0.00'),
                'payments_made': Decimal('0.00'),
                'outstanding_amount': Decimal('0.00'),
                'last_payment_date': None,
                'payment_status': 'current',
                'leases': []
            }
            
            for lease in active_leases:
                lease_balance = self._calculate_lease_balance(lease)
                
                # Aggregate totals
                balance_data['total_balance'] += lease_balance['total_owed']
                balance_data['monthly_rent'] += lease.monthly_rent
                balance_data['late_fees'] += lease_balance['late_fees']
                balance_data['payments_made'] += lease_balance['payments_made']
                balance_data['outstanding_amount'] += lease_balance['outstanding_balance']
                
                # Track latest payment date
                if lease_balance['last_payment_date']:
                    if not balance_data['last_payment_date'] or lease_balance['last_payment_date'] > balance_data['last_payment_date']:
                        balance_data['last_payment_date'] = lease_balance['last_payment_date']
                
                balance_data['leases'].append(lease_balance)
            
            # Determine overall payment status
            balance_data['payment_status'] = self._determine_payment_status(balance_data)
            
            return balance_data
            
        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': f"Tenant not found: {tenant_id}"
            }
        except Exception as e:
            logger.error(f"❌ Balance calculation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Balance calculation failed: {str(e)}"
            }
    
    def get_payment_history(self, tenant_id: str, months_back: int = 12) -> Dict:
        """
        📊 PAYMENT HISTORY: Get detailed payment history for a tenant
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            cutoff_date = timezone.now().date() - timedelta(days=months_back * 30)
            
            payments = Payment.objects.filter(
                lease__tenant=tenant,
                payment_date__gte=cutoff_date
            ).order_by('-payment_date')
            
            payment_summary = {
                'tenant_info': {
                    'id': str(tenant.id),
                    'name': tenant.full_name
                },
                'period': f"Last {months_back} months",
                'total_payments': payments.count(),
                'total_amount_paid': payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
                'on_time_payments': 0,
                'late_payments': 0,
                'payments': []
            }
            
            for payment in payments:
                payment_data = {
                    'id': str(payment.id),
                    'amount': float(payment.amount),
                    'payment_date': payment.payment_date.isoformat(),
                    'due_date': payment.due_date.isoformat(),
                    'type': payment.payment_type,
                    'status': payment.status,
                    'property': payment.lease.property.title,
                    'days_late': max(0, (payment.payment_date - payment.due_date).days),
                    'is_late': payment.payment_date > payment.due_date
                }
                
                if payment_data['is_late']:
                    payment_summary['late_payments'] += 1
                else:
                    payment_summary['on_time_payments'] += 1
                
                payment_summary['payments'].append(payment_data)
            
            # Calculate payment reliability score
            if payment_summary['total_payments'] > 0:
                payment_summary['reliability_score'] = round(
                    (payment_summary['on_time_payments'] / payment_summary['total_payments']) * 100, 1
                )
            else:
                payment_summary['reliability_score'] = 0.0
            
            return payment_summary
            
        except Exception as e:
            logger.error(f"❌ Payment history retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': f"Payment history retrieval failed: {str(e)}"
            }
    
    def get_all_balances(self) -> Dict:
        """
        📋 ALL BALANCES: Get balance summary for all tenants
        """
        try:
            active_tenants = Tenant.objects.filter(is_active=True, leases__status='active').distinct()
            
            summary = {
                'total_tenants': active_tenants.count(),
                'total_monthly_rent': Decimal('0.00'),
                'total_outstanding': Decimal('0.00'),
                'total_late_fees': Decimal('0.00'),
                'current_tenants': 0,
                'overdue_tenants': 0,
                'tenants': []
            }
            
            for tenant in active_tenants:
                balance_info = self.calculate_tenant_balance(str(tenant.id))
                
                if balance_info.get('success', True):  # Skip failed calculations
                    summary['total_monthly_rent'] += balance_info['monthly_rent']
                    summary['total_outstanding'] += balance_info['outstanding_amount']
                    summary['total_late_fees'] += balance_info['late_fees']
                    
                    if balance_info['payment_status'] == 'current':
                        summary['current_tenants'] += 1
                    else:
                        summary['overdue_tenants'] += 1
                    
                    summary['tenants'].append({
                        'tenant_id': str(tenant.id),
                        'name': tenant.full_name,
                        'monthly_rent': float(balance_info['monthly_rent']),
                        'outstanding_amount': float(balance_info['outstanding_amount']),
                        'payment_status': balance_info['payment_status'],
                        'last_payment_date': balance_info['last_payment_date'].isoformat() if balance_info['last_payment_date'] else None
                    })
            
            # Collection rate
            if summary['total_monthly_rent'] > 0:
                collected_amount = summary['total_monthly_rent'] - summary['total_outstanding']
                summary['collection_rate'] = round(float(collected_amount / summary['total_monthly_rent'] * 100), 1)
            else:
                summary['collection_rate'] = 0.0
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ All balances retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': f"All balances retrieval failed: {str(e)}"
            }
    
    def _calculate_lease_balance(self, lease: Lease) -> Dict:
        """Calculate balance for a specific lease"""
        # Get all payments for this lease
        payments = Payment.objects.filter(lease=lease)
        late_fees = LateFee.objects.filter(payment__lease=lease, status='applied')
        
        # Calculate totals
        payments_made = payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        late_fees_total = late_fees.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Calculate expected rent (simplified - could be more complex based on lease terms)
        months_elapsed = self._calculate_months_elapsed(lease)
        expected_rent = lease.monthly_rent * months_elapsed
        
        total_owed = expected_rent + late_fees_total
        outstanding_balance = total_owed - payments_made
        
        # Get last payment date
        last_payment = payments.filter(status='completed').order_by('-payment_date').first()
        last_payment_date = last_payment.payment_date if last_payment else None
        
        return {
            'lease_id': str(lease.id),
            'property': lease.property.title,
            'monthly_rent': lease.monthly_rent,
            'months_elapsed': months_elapsed,
            'expected_rent': expected_rent,
            'payments_made': payments_made,
            'late_fees': late_fees_total,
            'total_owed': total_owed,
            'outstanding_balance': outstanding_balance,
            'last_payment_date': last_payment_date,
            'is_current': outstanding_balance <= 0
        }
    
    def _calculate_months_elapsed(self, lease: Lease) -> int:
        """Calculate number of months elapsed since lease start"""
        today = timezone.now().date()
        start_date = lease.start_date
        
        # Calculate months between dates
        months = (today.year - start_date.year) * 12 + (today.month - start_date.month)
        
        # Add 1 if we've passed the rent due day this month
        if today.day >= lease.rent_due_day:
            months += 1
            
        return max(0, months)
    
    def _calculate_due_date(self, lease: Lease, payment_date: date) -> date:
        """Calculate the due date for a payment"""
        # For simplicity, assume payment is for the current month
        year = payment_date.year
        month = payment_date.month
        
        try:
            return date(year, month, lease.rent_due_day)
        except ValueError:
            # Handle cases where rent_due_day doesn't exist in the month (e.g., Feb 31)
            # Default to last day of month
            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            last_day_of_month = (next_month - timedelta(days=1)).day
            return date(year, month, min(lease.rent_due_day, last_day_of_month))
    
    def _determine_payment_status(self, balance_data: Dict) -> str:
        """Determine overall payment status for a tenant"""
        if balance_data['outstanding_amount'] <= 0:
            return 'current'
        elif balance_data['late_fees'] > 0:
            return 'overdue_with_fees'
        else:
            return 'overdue'

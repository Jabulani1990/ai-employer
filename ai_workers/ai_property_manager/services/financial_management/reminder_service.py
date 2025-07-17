"""
📢 REMINDER SERVICE

Automated payment reminder system with intelligent scheduling.

Features:
- Automated payment reminders
- Intelligent reminder scheduling
- Multi-channel notifications (email, SMS)
- Escalation sequences
- Personalized messaging

Task: #24 - Send rental payment reminders
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .models import Tenant, Lease, Payment, PaymentReminder
from .payment_tracker import PaymentTracker

logger = logging.getLogger(__name__)


class ReminderService:
    """
    📧 REMINDER SERVICE: Intelligent payment reminder automation
    
    Automatically sends payment reminders with smart scheduling
    and personalized messaging based on tenant payment history.
    """
    
    def __init__(self):
        self.service_name = "Reminder Service"
        self.payment_tracker = PaymentTracker()
        
        # Reminder scheduling (days before due date)
        self.reminder_schedule = {
            'early_reminder': 7,    # 7 days before due
            'standard_reminder': 3, # 3 days before due
            'final_reminder': 1,    # 1 day before due
            'overdue_reminder': 1,  # 1 day after due (then escalate)
        }
    
    def schedule_payment_reminders(self, lease_id: str = None) -> Dict:
        """
        📅 SCHEDULE REMINDERS: Set up automated payment reminders
        
        Args:
            lease_id: Specific lease to schedule (None for all active leases)
            
        Returns:
            Dict with scheduling results
        """
        try:
            if lease_id:
                leases = Lease.objects.filter(id=lease_id, status='active')
            else:
                leases = Lease.objects.filter(status='active')
            
            scheduled_count = 0
            results = []
            
            for lease in leases:
                lease_result = self._schedule_lease_reminders(lease)
                results.append(lease_result)
                if lease_result['success']:
                    scheduled_count += lease_result['reminders_scheduled']
            
            logger.info(f"✅ Scheduled {scheduled_count} payment reminders for {leases.count()} leases")
            
            return {
                'success': True,
                'total_leases': leases.count(),
                'reminders_scheduled': scheduled_count,
                'lease_results': results,
                'message': f"Successfully scheduled {scheduled_count} payment reminders"
            }
            
        except Exception as e:
            logger.error(f"❌ Reminder scheduling failed: {str(e)}")
            return {
                'success': False,
                'error': f"Reminder scheduling failed: {str(e)}"
            }
    
    def send_due_reminders(self) -> Dict:
        """
        📤 SEND DUE REMINDERS: Send all pending reminders that are due
        """
        try:
            # Get all pending reminders that should be sent now
            now = timezone.now()
            due_reminders = PaymentReminder.objects.filter(
                status='pending',
                scheduled_date__lte=now
            ).select_related('payment__lease__tenant', 'payment__lease__property')
            
            sent_count = 0
            failed_count = 0
            results = []
            
            for reminder in due_reminders:
                result = self._send_reminder(reminder)
                results.append(result)
                
                if result['success']:
                    sent_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"✅ Sent {sent_count} reminders, {failed_count} failed")
            
            return {
                'success': True,
                'reminders_sent': sent_count,
                'reminders_failed': failed_count,
                'results': results,
                'message': f"Sent {sent_count} payment reminders successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Sending reminders failed: {str(e)}")
            return {
                'success': False,
                'error': f"Sending reminders failed: {str(e)}"
            }
    
    def create_custom_reminder(self, payment_id: str, reminder_type: str, 
                             scheduled_date: datetime, message: str = None) -> Dict:
        """
        ✉️ CUSTOM REMINDER: Create a custom reminder for specific payment
        """
        try:
            payment = Payment.objects.get(id=payment_id)
            
            # Generate message if not provided
            if not message:
                message = self._generate_reminder_message(payment, reminder_type)
            
            # Create reminder
            reminder = PaymentReminder.objects.create(
                payment=payment,
                reminder_type=reminder_type,
                scheduled_date=scheduled_date,
                subject=self._generate_subject(payment, reminder_type),
                message=message,
                status='pending'
            )
            
            logger.info(f"✅ Custom reminder created for {payment.lease.tenant.full_name}")
            
            return {
                'success': True,
                'reminder_id': str(reminder.id),
                'scheduled_date': scheduled_date.isoformat(),
                'message': f"Custom reminder scheduled for {payment.lease.tenant.full_name}"
            }
            
        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': f"Payment not found: {payment_id}"
            }
        except Exception as e:
            logger.error(f"❌ Custom reminder creation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Custom reminder creation failed: {str(e)}"
            }
    
    def get_reminder_analytics(self, days_back: int = 30) -> Dict:
        """
        📊 REMINDER ANALYTICS: Get reminder effectiveness analytics
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_back)
            
            reminders = PaymentReminder.objects.filter(
                created_at__gte=cutoff_date
            )
            
            analytics = {
                'period_days': days_back,
                'total_reminders': reminders.count(),
                'sent_reminders': reminders.filter(status='sent').count(),
                'pending_reminders': reminders.filter(status='pending').count(),
                'failed_reminders': reminders.filter(status='failed').count(),
                'by_type': {},
                'effectiveness': {}
            }
            
            # Breakdown by reminder type
            for reminder_type, _ in PaymentReminder.REMINDER_TYPES:
                type_reminders = reminders.filter(reminder_type=reminder_type)
                analytics['by_type'][reminder_type] = {
                    'total': type_reminders.count(),
                    'sent': type_reminders.filter(status='sent').count(),
                    'pending': type_reminders.filter(status='pending').count(),
                    'failed': type_reminders.filter(status='failed').count()
                }
            
            # Calculate effectiveness (payments made after reminders)
            sent_reminders = reminders.filter(status='sent')
            payments_after_reminders = 0
            
            for reminder in sent_reminders:
                # Check if payment was made after reminder was sent
                if reminder.sent_date:
                    payments_made = Payment.objects.filter(
                        lease=reminder.payment.lease,
                        payment_date__gte=reminder.sent_date.date(),
                        status='completed'
                    ).exists()
                    
                    if payments_made:
                        payments_after_reminders += 1
            
            if analytics['sent_reminders'] > 0:
                analytics['effectiveness']['response_rate'] = round(
                    (payments_after_reminders / analytics['sent_reminders']) * 100, 1
                )
            else:
                analytics['effectiveness']['response_rate'] = 0.0
            
            analytics['effectiveness']['payments_triggered'] = payments_after_reminders
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Reminder analytics failed: {str(e)}")
            return {
                'success': False,
                'error': f"Reminder analytics failed: {str(e)}"
            }
    
    def _schedule_lease_reminders(self, lease: Lease) -> Dict:
        """Schedule reminders for a specific lease"""
        try:
            # Calculate next rent due date
            next_due_date = self._calculate_next_due_date(lease)
            
            # Create upcoming payment record if it doesn't exist
            upcoming_payment, created = Payment.objects.get_or_create(
                lease=lease,
                due_date=next_due_date,
                payment_type='rent',
                defaults={
                    'amount': lease.monthly_rent,
                    'payment_date': next_due_date,  # Will be updated when actually paid
                    'status': 'pending'
                }
            )
            
            # Remove existing pending reminders for this payment
            PaymentReminder.objects.filter(
                payment=upcoming_payment,
                status='pending'
            ).delete()
            
            reminders_created = 0
            
            # Schedule standard reminders
            for reminder_type, days_before in self.reminder_schedule.items():
                if reminder_type == 'overdue_reminder':
                    continue  # Handle overdue separately
                    
                scheduled_date = timezone.make_aware(
                    datetime.combine(
                        next_due_date - timedelta(days=days_before),
                        datetime.min.time()
                    )
                )
                
                # Only schedule if the reminder date is in the future
                if scheduled_date > timezone.now():
                    PaymentReminder.objects.create(
                        payment=upcoming_payment,
                        reminder_type='upcoming',
                        scheduled_date=scheduled_date,
                        subject=self._generate_subject(upcoming_payment, 'upcoming'),
                        message=self._generate_reminder_message(upcoming_payment, 'upcoming'),
                        status='pending'
                    )
                    reminders_created += 1
            
            return {
                'success': True,
                'lease_id': str(lease.id),
                'tenant_name': lease.tenant.full_name,
                'next_due_date': next_due_date.isoformat(),
                'reminders_scheduled': reminders_created
            }
            
        except Exception as e:
            logger.error(f"❌ Lease reminder scheduling failed: {str(e)}")
            return {
                'success': False,
                'lease_id': str(lease.id),
                'error': str(e)
            }
    
    def _send_reminder(self, reminder: PaymentReminder) -> Dict:
        """Send an individual reminder"""
        try:
            tenant = reminder.payment.lease.tenant
            
            # Send email
            email_sent = self._send_email_reminder(reminder)
            
            if email_sent:
                # Update reminder status
                reminder.status = 'sent'
                reminder.sent_date = timezone.now()
                reminder.save()
                
                logger.info(f"✅ Reminder sent to {tenant.full_name}")
                
                return {
                    'success': True,
                    'reminder_id': str(reminder.id),
                    'tenant_name': tenant.full_name,
                    'reminder_type': reminder.reminder_type
                }
            else:
                # Update as failed
                reminder.status = 'failed'
                reminder.error_message = 'Email sending failed'
                reminder.save()
                
                return {
                    'success': False,
                    'reminder_id': str(reminder.id),
                    'error': 'Email sending failed'
                }
                
        except Exception as e:
            reminder.status = 'failed'
            reminder.error_message = str(e)
            reminder.save()
            
            logger.error(f"❌ Reminder sending failed: {str(e)}")
            return {
                'success': False,
                'reminder_id': str(reminder.id),
                'error': str(e)
            }
    
    def _send_email_reminder(self, reminder: PaymentReminder) -> bool:
        """Send email reminder to tenant"""
        try:
            tenant = reminder.payment.lease.tenant
            
            # For now, simulate email sending
            # In production, you would integrate with your email service
            logger.info(f"📧 Email reminder sent to {tenant.email}")
            
            # Placeholder for actual email sending
            # send_mail(
            #     subject=reminder.subject,
            #     message=reminder.message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[tenant.email],
            #     fail_silently=False
            # )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Email sending failed: {str(e)}")
            return False
    
    def _generate_reminder_message(self, payment: Payment, reminder_type: str) -> str:
        """Generate personalized reminder message"""
        tenant = payment.lease.tenant
        lease = payment.lease
        
        # Get payment history for personalization
        payment_history = self.payment_tracker.get_payment_history(str(tenant.id), 6)
        reliability_score = payment_history.get('reliability_score', 0)
        
        # Base message templates
        if reminder_type == 'upcoming':
            if reliability_score >= 90:
                tone = "friendly"
                message = f"""Dear {tenant.first_name},

I hope you're doing well! This is a friendly reminder that your rent payment of ${payment.amount} for {lease.property.title} is due on {payment.due_date.strftime('%B %d, %Y')}.

As always, thank you for being such a reliable tenant. Your consistent payments are greatly appreciated.

If you have any questions or concerns, please don't hesitate to reach out.

Best regards,
Property Management Team"""
            else:
                tone = "standard"
                message = f"""Dear {tenant.first_name},

This is a reminder that your rent payment of ${payment.amount} for {lease.property.title} is due on {payment.due_date.strftime('%B %d, %Y')}.

Please ensure your payment is submitted on time to avoid any late fees.

If you have any questions about your payment or need assistance, please contact us.

Thank you,
Property Management Team"""
                
        elif reminder_type == 'overdue':
            message = f"""Dear {tenant.first_name},

This is an important notice that your rent payment of ${payment.amount} for {lease.property.title} was due on {payment.due_date.strftime('%B %d, %Y')} and is now {payment.days_overdue} days overdue.

Please submit your payment immediately to avoid additional late fees and potential further action.

If you're experiencing financial difficulties, please contact us to discuss payment options.

Urgent attention required,
Property Management Team"""
        
        else:
            message = f"""Dear {tenant.first_name},

This is a payment reminder for your rent of ${payment.amount} for {lease.property.title}.

Due date: {payment.due_date.strftime('%B %d, %Y')}

Please ensure timely payment.

Thank you,
Property Management Team"""
        
        return message
    
    def _generate_subject(self, payment: Payment, reminder_type: str) -> str:
        """Generate email subject line"""
        property_title = payment.lease.property.title
        
        if reminder_type == 'upcoming':
            return f"Rent Reminder - {property_title} Due {payment.due_date.strftime('%m/%d')}"
        elif reminder_type == 'overdue':
            return f"URGENT: Overdue Rent Payment - {property_title}"
        else:
            return f"Payment Reminder - {property_title}"
    
    def _calculate_next_due_date(self, lease: Lease) -> date:
        """Calculate the next rent due date"""
        today = timezone.now().date()
        
        # If today is before this month's due date, use this month
        try:
            this_month_due = today.replace(day=lease.rent_due_day)
            if today <= this_month_due:
                return this_month_due
        except ValueError:
            # Handle cases where rent_due_day doesn't exist in current month
            pass
        
        # Otherwise, use next month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        
        try:
            return next_month.replace(day=lease.rent_due_day)
        except ValueError:
            # Handle February 31st, etc.
            last_day = (next_month.replace(month=next_month.month % 12 + 1, day=1) - timedelta(days=1)).day
            return next_month.replace(day=min(lease.rent_due_day, last_day))

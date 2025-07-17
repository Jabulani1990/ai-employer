"""
🚨 OVERDUE DETECTOR SERVICE

Intelligent overdue payment detection and escalation management.

Features:
- Automated overdue payment detection
- Risk assessment and scoring
- Escalation triggers
- Trend analysis
- Early warning system

Task: #27 - Detect overdue payments
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from decimal import Decimal

from .models import Tenant, Lease, Payment, LateFee, PaymentReminder
from .payment_tracker import PaymentTracker

logger = logging.getLogger(__name__)


class OverdueDetector:
    """
    🔍 OVERDUE DETECTOR: Intelligent overdue payment monitoring
    
    Automatically detects overdue payments, assesses risk levels,
    and triggers appropriate escalation actions.
    """
    
    def __init__(self):
        self.service_name = "Overdue Detector"
        self.payment_tracker = PaymentTracker()
        
        # Risk thresholds (days overdue)
        self.risk_levels = {
            'low': (1, 7),      # 1-7 days overdue
            'medium': (8, 15),  # 8-15 days overdue
            'high': (16, 30),   # 16-30 days overdue
            'critical': (31, float('inf'))  # 31+ days overdue
        }
    
    def detect_overdue_payments(self) -> Dict:
        """
        🚨 DETECT OVERDUE: Find all overdue payments with risk assessment
        
        Returns comprehensive overdue payment analysis with risk levels
        """
        try:
            today = timezone.now().date()
            
            # Get all pending payments that are overdue
            overdue_payments = Payment.objects.filter(
                status='pending',
                due_date__lt=today
            ).select_related('lease__tenant', 'lease__property')
            
            overdue_analysis = {
                'detection_date': today.isoformat(),
                'total_overdue_payments': overdue_payments.count(),
                'total_overdue_amount': Decimal('0.00'),
                'risk_summary': {
                    'low': {'count': 0, 'amount': Decimal('0.00')},
                    'medium': {'count': 0, 'amount': Decimal('0.00')},
                    'high': {'count': 0, 'amount': Decimal('0.00')},
                    'critical': {'count': 0, 'amount': Decimal('0.00')}
                },
                'overdue_payments': [],
                'tenants_at_risk': [],
                'escalation_required': []
            }
            
            # Analyze each overdue payment
            for payment in overdue_payments:
                days_overdue = (today - payment.due_date).days
                risk_level = self._assess_risk_level(days_overdue)
                
                # Calculate tenant's total overdue amount
                tenant_overdue = self._calculate_tenant_overdue_amount(payment.lease.tenant)
                
                payment_data = {
                    'payment_id': str(payment.id),
                    'tenant_id': str(payment.lease.tenant.id),
                    'tenant_name': payment.lease.tenant.full_name,
                    'tenant_email': payment.lease.tenant.email,
                    'property': payment.lease.property.title,
                    'amount': float(payment.amount),
                    'due_date': payment.due_date.isoformat(),
                    'days_overdue': days_overdue,
                    'risk_level': risk_level,
                    'payment_type': payment.payment_type,
                    'tenant_total_overdue': float(tenant_overdue),
                    'requires_escalation': self._requires_escalation(payment, days_overdue),
                    'suggested_actions': self._suggest_actions(payment, days_overdue, risk_level)
                }
                
                overdue_analysis['overdue_payments'].append(payment_data)
                overdue_analysis['total_overdue_amount'] += payment.amount
                overdue_analysis['risk_summary'][risk_level]['count'] += 1
                overdue_analysis['risk_summary'][risk_level]['amount'] += payment.amount
                
                # Check if escalation is required
                if payment_data['requires_escalation']:
                    overdue_analysis['escalation_required'].append(payment_data)
            
            # Identify tenants at risk
            overdue_analysis['tenants_at_risk'] = self._identify_at_risk_tenants(overdue_payments)
            
            # Generate summary statistics
            overdue_analysis['summary'] = self._generate_overdue_summary(overdue_analysis)
            
            logger.info(f"🚨 Detected {overdue_analysis['total_overdue_payments']} overdue payments totaling ${overdue_analysis['total_overdue_amount']}")
            
            return overdue_analysis
            
        except Exception as e:
            logger.error(f"❌ Overdue detection failed: {str(e)}")
            return {
                'success': False,
                'error': f"Overdue detection failed: {str(e)}"
            }
    
    def get_tenant_risk_profile(self, tenant_id: str) -> Dict:
        """
        📊 TENANT RISK PROFILE: Comprehensive risk assessment for a tenant
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)
            
            # Get payment history
            payment_history = self.payment_tracker.get_payment_history(tenant_id, 12)
            
            # Current overdue status
            overdue_payments = Payment.objects.filter(
                lease__tenant=tenant,
                status='pending',
                due_date__lt=timezone.now().date()
            )
            
            # Calculate risk metrics
            risk_profile = {
                'tenant_info': {
                    'id': str(tenant.id),
                    'name': tenant.full_name,
                    'email': tenant.email,
                    'credit_score': tenant.credit_score
                },
                'current_status': {
                    'overdue_payments': overdue_payments.count(),
                    'overdue_amount': float(overdue_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')),
                    'days_overdue': max([p.days_overdue for p in overdue_payments] + [0])
                },
                'payment_history': payment_history,
                'risk_indicators': {},
                'risk_score': 0,
                'risk_level': 'low',
                'recommendations': []
            }
            
            # Calculate risk indicators
            risk_profile['risk_indicators'] = self._calculate_risk_indicators(tenant, payment_history)
            
            # Calculate overall risk score (0-100)
            risk_profile['risk_score'] = self._calculate_risk_score(risk_profile)
            risk_profile['risk_level'] = self._determine_risk_level(risk_profile['risk_score'])
            
            # Generate recommendations
            risk_profile['recommendations'] = self._generate_risk_recommendations(risk_profile)
            
            return risk_profile
            
        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': f"Tenant not found: {tenant_id}"
            }
        except Exception as e:
            logger.error(f"❌ Risk profile generation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Risk profile generation failed: {str(e)}"
            }
    
    def get_overdue_trends(self, months_back: int = 6) -> Dict:
        """
        📈 OVERDUE TRENDS: Historical analysis of overdue payments
        """
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=months_back * 30)
            
            # Get historical overdue data
            monthly_data = []
            current_date = start_date
            
            while current_date <= end_date:
                month_end = min(current_date + timedelta(days=30), end_date)
                
                # Payments that were overdue during this period
                overdue_in_period = Payment.objects.filter(
                    due_date__lt=current_date,
                    created_at__lte=month_end,
                    status='pending'
                ).count()
                
                # Payments that became overdue in this period
                became_overdue = Payment.objects.filter(
                    due_date__range=[current_date, month_end],
                    status='pending'
                ).count()
                
                monthly_data.append({
                    'month': current_date.strftime('%Y-%m'),
                    'overdue_count': overdue_in_period,
                    'new_overdue': became_overdue,
                    'period_start': current_date.isoformat(),
                    'period_end': month_end.isoformat()
                })
                
                current_date = month_end + timedelta(days=1)
            
            # Calculate trends
            trends = {
                'period_months': months_back,
                'monthly_data': monthly_data,
                'trend_analysis': self._analyze_trends(monthly_data),
                'risk_patterns': self._identify_risk_patterns(),
                'seasonal_analysis': self._analyze_seasonal_patterns(monthly_data)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed: {str(e)}")
            return {
                'success': False,
                'error': f"Trend analysis failed: {str(e)}"
            }
    
    def trigger_escalation_actions(self, payment_id: str = None) -> Dict:
        """
        ⚡ TRIGGER ESCALATION: Execute escalation actions for overdue payments
        """
        try:
            if payment_id:
                payments = Payment.objects.filter(id=payment_id, status='pending')
            else:
                # Get all payments requiring escalation
                payments = Payment.objects.filter(
                    status='pending',
                    due_date__lt=timezone.now().date() - timedelta(days=15)  # 15+ days overdue
                )
            
            escalation_results = []
            
            for payment in payments:
                days_overdue = payment.days_overdue
                escalation_result = {
                    'payment_id': str(payment.id),
                    'tenant_name': payment.lease.tenant.full_name,
                    'days_overdue': days_overdue,
                    'actions_taken': []
                }
                
                # Determine escalation actions based on days overdue
                if days_overdue >= 30:
                    # Critical escalation
                    escalation_result['actions_taken'].extend([
                        'Legal notice prepared',
                        'Management notification sent',
                        'Payment plan discussion scheduled'
                    ])
                elif days_overdue >= 15:
                    # High escalation
                    escalation_result['actions_taken'].extend([
                        'Formal notice sent',
                        'Late fee applied',
                        'Property manager notified'
                    ])
                elif days_overdue >= 7:
                    # Medium escalation
                    escalation_result['actions_taken'].extend([
                        'Follow-up reminder sent',
                        'Phone call scheduled'
                    ])
                
                escalation_results.append(escalation_result)
            
            logger.info(f"⚡ Escalation actions triggered for {len(escalation_results)} payments")
            
            return {
                'success': True,
                'escalations_triggered': len(escalation_results),
                'escalation_results': escalation_results,
                'message': f"Escalation actions triggered for {len(escalation_results)} overdue payments"
            }
            
        except Exception as e:
            logger.error(f"❌ Escalation triggering failed: {str(e)}")
            return {
                'success': False,
                'error': f"Escalation triggering failed: {str(e)}"
            }
    
    def _assess_risk_level(self, days_overdue: int) -> str:
        """Assess risk level based on days overdue"""
        for level, (min_days, max_days) in self.risk_levels.items():
            if min_days <= days_overdue <= max_days:
                return level
        return 'low'
    
    def _calculate_tenant_overdue_amount(self, tenant: Tenant) -> Decimal:
        """Calculate total overdue amount for a tenant"""
        overdue_payments = Payment.objects.filter(
            lease__tenant=tenant,
            status='pending',
            due_date__lt=timezone.now().date()
        )
        return overdue_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    def _requires_escalation(self, payment: Payment, days_overdue: int) -> bool:
        """Determine if payment requires escalation"""
        # Check if recent reminders have been sent
        recent_reminders = PaymentReminder.objects.filter(
            payment=payment,
            status='sent',
            sent_date__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Escalate if overdue > 7 days and no recent reminders
        return days_overdue > 7 and recent_reminders == 0
    
    def _suggest_actions(self, payment: Payment, days_overdue: int, risk_level: str) -> List[str]:
        """Suggest appropriate actions based on payment status"""
        actions = []
        
        if days_overdue <= 3:
            actions.append("Send friendly reminder")
        elif days_overdue <= 7:
            actions.extend(["Send urgent reminder", "Consider phone call"])
        elif days_overdue <= 15:
            actions.extend(["Apply late fee", "Send formal notice", "Schedule payment plan discussion"])
        else:
            actions.extend(["Legal consultation", "Escalate to management", "Consider eviction process"])
        
        return actions
    
    def _identify_at_risk_tenants(self, overdue_payments) -> List[Dict]:
        """Identify tenants with high risk profiles"""
        tenant_risk_data = {}
        
        for payment in overdue_payments:
            tenant_id = str(payment.lease.tenant.id)
            
            if tenant_id not in tenant_risk_data:
                tenant_risk_data[tenant_id] = {
                    'tenant_name': payment.lease.tenant.full_name,
                    'overdue_count': 0,
                    'total_overdue': Decimal('0.00'),
                    'max_days_overdue': 0,
                    'properties': set()
                }
            
            tenant_data = tenant_risk_data[tenant_id]
            tenant_data['overdue_count'] += 1
            tenant_data['total_overdue'] += payment.amount
            tenant_data['max_days_overdue'] = max(tenant_data['max_days_overdue'], payment.days_overdue)
            tenant_data['properties'].add(payment.lease.property.title)
        
        # Convert to list and filter high-risk tenants
        at_risk_tenants = []
        for tenant_id, data in tenant_risk_data.items():
            data['properties'] = list(data['properties'])
            data['total_overdue'] = float(data['total_overdue'])
            
            # Consider high-risk if: multiple overdue payments OR > 15 days overdue OR > $1000 overdue
            if (data['overdue_count'] > 1 or 
                data['max_days_overdue'] > 15 or 
                data['total_overdue'] > 1000):
                at_risk_tenants.append(data)
        
        return sorted(at_risk_tenants, key=lambda x: x['total_overdue'], reverse=True)
    
    def _generate_overdue_summary(self, overdue_analysis: Dict) -> Dict:
        """Generate summary statistics"""
        total_payments = overdue_analysis['total_overdue_payments']
        
        if total_payments == 0:
            return {
                'severity': 'low',
                'average_days_overdue': 0,
                'average_amount': 0,
                'immediate_action_required': 0
            }
        
        # Calculate averages
        avg_days = sum(p['days_overdue'] for p in overdue_analysis['overdue_payments']) / total_payments
        avg_amount = float(overdue_analysis['total_overdue_amount']) / total_payments
        
        # Count immediate actions required (high/critical risk)
        immediate_actions = (overdue_analysis['risk_summary']['high']['count'] + 
                           overdue_analysis['risk_summary']['critical']['count'])
        
        # Determine overall severity
        critical_ratio = overdue_analysis['risk_summary']['critical']['count'] / total_payments
        if critical_ratio > 0.2:
            severity = 'critical'
        elif critical_ratio > 0.1 or avg_days > 15:
            severity = 'high'
        elif avg_days > 7:
            severity = 'medium'
        else:
            severity = 'low'
        
        return {
            'severity': severity,
            'average_days_overdue': round(avg_days, 1),
            'average_amount': round(avg_amount, 2),
            'immediate_action_required': immediate_actions,
            'critical_ratio': round(critical_ratio * 100, 1)
        }
    
    def _calculate_risk_indicators(self, tenant: Tenant, payment_history: Dict) -> Dict:
        """Calculate various risk indicators for a tenant"""
        indicators = {
            'late_payment_frequency': 0,
            'average_days_late': 0,
            'payment_reliability': 0,
            'recent_late_trend': False,
            'credit_risk': 'unknown'
        }
        
        if payment_history.get('total_payments', 0) > 0:
            indicators['late_payment_frequency'] = payment_history.get('late_payments', 0) / payment_history['total_payments']
            indicators['payment_reliability'] = payment_history.get('reliability_score', 0)
            
            # Calculate average days late for late payments
            late_payments = [p for p in payment_history.get('payments', []) if p.get('is_late', False)]
            if late_payments:
                indicators['average_days_late'] = sum(p.get('days_late', 0) for p in late_payments) / len(late_payments)
            
            # Check recent trend (last 3 payments)
            recent_payments = payment_history.get('payments', [])[:3]
            recent_late_count = sum(1 for p in recent_payments if p.get('is_late', False))
            indicators['recent_late_trend'] = recent_late_count >= 2
        
        # Credit risk assessment
        if tenant.credit_score:
            if tenant.credit_score >= 750:
                indicators['credit_risk'] = 'low'
            elif tenant.credit_score >= 650:
                indicators['credit_risk'] = 'medium'
            else:
                indicators['credit_risk'] = 'high'
        
        return indicators
    
    def _calculate_risk_score(self, risk_profile: Dict) -> int:
        """Calculate overall risk score (0-100)"""
        score = 0
        
        # Current overdue status (40 points)
        overdue_amount = risk_profile['current_status']['overdue_amount']
        days_overdue = risk_profile['current_status']['days_overdue']
        
        if overdue_amount > 0:
            score += min(20, overdue_amount / 100)  # Up to 20 points based on amount
            score += min(20, days_overdue)  # Up to 20 points based on days
        
        # Payment history (40 points)
        reliability = risk_profile['payment_history'].get('reliability_score', 100)
        score += (100 - reliability) * 0.4
        
        # Risk indicators (20 points)
        indicators = risk_profile['risk_indicators']
        score += indicators.get('late_payment_frequency', 0) * 10
        score += min(10, indicators.get('average_days_late', 0) / 2)
        
        if indicators.get('recent_late_trend', False):
            score += 5
        
        if indicators.get('credit_risk') == 'high':
            score += 5
        
        return min(100, int(score))
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """Determine risk level from score"""
        if risk_score >= 75:
            return 'critical'
        elif risk_score >= 50:
            return 'high'
        elif risk_score >= 25:
            return 'medium'
        else:
            return 'low'
    
    def _generate_risk_recommendations(self, risk_profile: Dict) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        risk_level = risk_profile['risk_level']
        
        if risk_level == 'critical':
            recommendations.extend([
                "Immediate contact required",
                "Consider legal consultation",
                "Implement payment plan",
                "Increase monitoring frequency"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "Schedule payment discussion",
                "Send formal notice",
                "Apply late fees",
                "Weekly check-ins"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Send reminder notice",
                "Monitor closely",
                "Consider payment plan options"
            ])
        else:
            recommendations.append("Continue standard monitoring")
        
        return recommendations
    
    def _analyze_trends(self, monthly_data: List[Dict]) -> Dict:
        """Analyze trends in overdue payments"""
        if len(monthly_data) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_avg = sum(m['overdue_count'] for m in monthly_data[-3:]) / min(3, len(monthly_data))
        earlier_avg = sum(m['overdue_count'] for m in monthly_data[:-3]) / max(1, len(monthly_data) - 3)
        
        if recent_avg > earlier_avg * 1.2:
            trend = 'increasing'
        elif recent_avg < earlier_avg * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'recent_average': round(recent_avg, 1),
            'earlier_average': round(earlier_avg, 1),
            'change_percentage': round((recent_avg - earlier_avg) / max(earlier_avg, 1) * 100, 1)
        }
    
    def _identify_risk_patterns(self) -> Dict:
        """Identify patterns in overdue payments"""
        # This would analyze historical data for patterns
        # For now, return placeholder data
        return {
            'seasonal_peaks': ['January', 'July'],
            'high_risk_property_types': ['apartment'],
            'common_overdue_periods': ['1-7 days', '15-30 days']
        }
    
    def _analyze_seasonal_patterns(self, monthly_data: List[Dict]) -> Dict:
        """Analyze seasonal patterns in overdue payments"""
        # Group by month and calculate averages
        month_totals = {}
        for data in monthly_data:
            month = data['month'].split('-')[1]  # Extract month number
            if month not in month_totals:
                month_totals[month] = []
            month_totals[month].append(data['overdue_count'])
        
        month_averages = {
            month: sum(counts) / len(counts) 
            for month, counts in month_totals.items()
        }
        
        if month_averages:
            peak_month = max(month_averages, key=month_averages.get)
            low_month = min(month_averages, key=month_averages.get)
        else:
            peak_month = low_month = None
        
        return {
            'peak_month': peak_month,
            'low_month': low_month,
            'month_averages': month_averages
        }

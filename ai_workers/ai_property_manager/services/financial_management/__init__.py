"""
💰 FINANCIAL MANAGEMENT SERVICE PACKAGE

Comprehensive financial management for property management including:
- Payment tracking and monitoring
- Automated rent collection reminders
- Late fee management
- Financial reporting and analytics
- Overdue payment detection

This package provides autonomous financial management capabilities
that learn and adapt to improve collection rates and reporting accuracy.
"""

# Note: Import services only when needed to avoid circular imports
# from .payment_tracker import PaymentTracker
# from .reminder_service import ReminderService
# from .overdue_detector import OverdueDetector
# from .report_generator import ReportGenerator
# from .late_fee_manager import LateFeeManager

__version__ = '1.0.0'
__author__ = 'AI Property Manager'

# Expose main service classes when imported
def get_payment_tracker():
    from .payment_tracker import PaymentTracker
    return PaymentTracker

def get_reminder_service():
    from .reminder_service import ReminderService
    return ReminderService

def get_overdue_detector():
    from .overdue_detector import OverdueDetector
    return OverdueDetector

def get_report_generator():
    from .report_generator import ReportGenerator
    return ReportGenerator

def get_late_fee_manager():
    from .late_fee_manager import LateFeeManager
    return LateFeeManager

# Autonomous Financial Management System
class FinancialManagementSystem:
    """
    🤖 AUTONOMOUS FINANCIAL MANAGEMENT SYSTEM
    
    Coordinates all financial management services with AI-driven optimization
    """
    
    def __init__(self):
        self._payment_tracker = None
        self._reminder_service = None
        self._overdue_detector = None
        self._report_generator = None
        self._late_fee_manager = None
    
    @property
    def payment_tracker(self):
        if self._payment_tracker is None:
            self._payment_tracker = get_payment_tracker()()
        return self._payment_tracker
    
    @property
    def reminder_service(self):
        if self._reminder_service is None:
            self._reminder_service = get_reminder_service()()
        return self._reminder_service
    
    @property
    def overdue_detector(self):
        if self._overdue_detector is None:
            self._overdue_detector = get_overdue_detector()()
        return self._overdue_detector
    
    @property
    def report_generator(self):
        if self._report_generator is None:
            self._report_generator = get_report_generator()()
        return self._report_generator
    
    @property
    def late_fee_manager(self):
        if self._late_fee_manager is None:
            self._late_fee_manager = get_late_fee_manager()()
        return self._late_fee_manager

# Global instance
financial_system = FinancialManagementSystem()
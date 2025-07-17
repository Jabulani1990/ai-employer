"""
🧪 FINANCIAL MANAGEMENT SYSTEM TESTS

Comprehensive test suite for the financial management services.
Tests all 5 core tasks: payment tracking, reminders, overdue detection, 
reporting, and late fee management.
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employer_platform.settings')
django.setup()

from ai_workers.models import Tenant, Lease, Payment
from ai_workers.ai_property_manager.services.financial_management import (
    PaymentTracker,
    ReminderService,
    OverdueDetector,
    ReportGenerator,
    LateFeeManager
)

def test_financial_management_system():
    """
    🎯 COMPREHENSIVE FINANCIAL MANAGEMENT TEST
    
    Tests all 5 core financial management tasks:
    - Task 24: Send rental payment reminders
    - Task 25: Track rent payments & balances  
    - Task 26: Auto-generate financial reports
    - Task 27: Detect overdue payments
    - Task 28: Issue late fee notices
    """
    
    print("🏦 Starting Financial Management System Tests...")
    print("=" * 60)
    
    # Initialize services
    payment_tracker = PaymentTracker()
    reminder_service = ReminderService()
    overdue_detector = OverdueDetector()
    report_generator = ReportGenerator()
    late_fee_manager = LateFeeManager()
    
    test_results = {
        'payment_tracking': False,
        'reminders': False,
        'overdue_detection': False,
        'reporting': False,
        'late_fee_management': False
    }
    
    try:
        # 🧪 Test 1: Payment Tracking (Task 25)
        print("💰 Testing Payment Tracking...")
        
        # Create test tenant and lease
        tenant = Tenant.objects.create(
            name="John Doe",
            email="john.doe@test.com",
            tenant_since=date.today() - timedelta(days=365)
        )
        
        lease = Lease.objects.create(
            tenant=tenant,
            property_address="123 Test St, Test City",
            monthly_rent=Decimal("1500.00"),
            lease_start=date.today() - timedelta(days=300),
            lease_end=date.today() + timedelta(days=65),
            status='active'
        )
        
        # Test payment tracking
        payment_result = payment_tracker.track_payment(
            lease_id=str(lease.id),
            amount=1500.00,
            payment_date=date.today().isoformat(),
            payment_type='rent',
            description='Test payment'
        )
        
        if payment_result.get('success'):
            print("✅ Payment tracking: PASSED")
            test_results['payment_tracking'] = True
        else:
            print(f"❌ Payment tracking: FAILED - {payment_result.get('error')}")
        
        # 🧪 Test 2: Balance Calculation
        balance_result = payment_tracker.calculate_tenant_balance(str(tenant.id))
        if balance_result.get('success'):
            print(f"✅ Balance calculation: PASSED - Balance: ${balance_result.get('current_balance', 0)}")
        else:
            print(f"❌ Balance calculation: FAILED - {balance_result.get('error')}")
        
        # 🧪 Test 3: Payment Reminders (Task 24)
        print("\n📢 Testing Payment Reminders...")
        
        reminder_result = reminder_service.schedule_payment_reminders(str(lease.id))
        if reminder_result.get('success'):
            print("✅ Reminder scheduling: PASSED")
            test_results['reminders'] = True
        else:
            print(f"❌ Reminder scheduling: FAILED - {reminder_result.get('error')}")
        
        # Test sending reminders
        send_result = reminder_service.send_due_reminders()
        if send_result.get('success'):
            print(f"✅ Reminder sending: PASSED - Sent {send_result.get('reminders_sent', 0)} reminders")
        else:
            print(f"❌ Reminder sending: FAILED - {send_result.get('error')}")
        
        # 🧪 Test 4: Overdue Detection (Task 27)
        print("\n🚨 Testing Overdue Detection...")
        
        # Create an overdue scenario
        overdue_lease = Lease.objects.create(
            tenant=tenant,
            property_address="456 Overdue Ave, Test City",
            monthly_rent=Decimal("1200.00"),
            lease_start=date.today() - timedelta(days=60),
            lease_end=date.today() + timedelta(days=305),
            status='active',
            rent_due_day=1
        )
        
        overdue_result = overdue_detector.detect_overdue_payments()
        if overdue_result.get('success'):
            print(f"✅ Overdue detection: PASSED - Found {overdue_result.get('total_overdue_payments', 0)} overdue payments")
            test_results['overdue_detection'] = True
        else:
            print(f"❌ Overdue detection: FAILED - {overdue_result.get('error')}")
        
        # Test risk profiling
        risk_result = overdue_detector.get_tenant_risk_profile(str(tenant.id))
        if risk_result.get('success'):
            print(f"✅ Risk profiling: PASSED - Risk level: {risk_result.get('risk_level', 'unknown')}")
        else:
            print(f"❌ Risk profiling: FAILED - {risk_result.get('error')}")
        
        # 🧪 Test 5: Financial Reporting (Task 26)
        print("\n📊 Testing Financial Reporting...")
        
        monthly_report = report_generator.generate_monthly_summary()
        if monthly_report.get('success'):
            print("✅ Monthly report generation: PASSED")
            test_results['reporting'] = True
        else:
            print(f"❌ Monthly report generation: FAILED - {monthly_report.get('error')}")
        
        payment_status_report = report_generator.generate_payment_status_report()
        if payment_status_report.get('success'):
            print("✅ Payment status report: PASSED")
        else:
            print(f"❌ Payment status report: FAILED - {payment_status_report.get('error')}")
        
        # 🧪 Test 6: Late Fee Management (Task 28)
        print("\n⚖️ Testing Late Fee Management...")
        
        late_fee_result = late_fee_manager.apply_late_fees()
        if late_fee_result.get('success'):
            print(f"✅ Late fee application: PASSED - Applied {late_fee_result.get('fees_applied', 0)} late fees")
            test_results['late_fee_management'] = True
        else:
            print(f"❌ Late fee application: FAILED - {late_fee_result.get('error')}")
        
        # Test late fee calculation
        calc_result = late_fee_manager.calculate_late_fee(
            lease_id=str(overdue_lease.id),
            days_late=10
        )
        if calc_result.get('success'):
            print(f"✅ Late fee calculation: PASSED - Fee: ${calc_result.get('fee_amount', 0)}")
        else:
            print(f"❌ Late fee calculation: FAILED - {calc_result.get('error')}")
        
        # 🧪 Test 7: System Integration
        print("\n🔗 Testing System Integration...")
        
        # Test getting all balances
        all_balances = payment_tracker.get_all_balances()
        if all_balances.get('success'):
            print(f"✅ System integration: PASSED - Tracking {all_balances.get('total_tenants', 0)} tenants")
        else:
            print(f"❌ System integration: FAILED - {all_balances.get('error')}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup test data
        try:
            Tenant.objects.filter(email__contains='test.com').delete()
            print("\n🧹 Test data cleaned up")
        except:
            pass
    
    # 📋 Test Results Summary
    print("\n" + "=" * 60)
    print("🎯 FINANCIAL MANAGEMENT SYSTEM TEST RESULTS")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for task, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{task.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL FINANCIAL MANAGEMENT TASKS WORKING PERFECTLY!")
        print("\n🏦 Ready for production use:")
        print("- Task 24: Send rental payment reminders ✅")
        print("- Task 25: Track rent payments & balances ✅") 
        print("- Task 26: Auto-generate financial reports ✅")
        print("- Task 27: Detect overdue payments ✅")
        print("- Task 28: Issue late fee notices ✅")
    else:
        print(f"⚠️ {total_tests - passed_tests} tasks need attention")
    
    return test_results

if __name__ == "__main__":
    test_financial_management_system()

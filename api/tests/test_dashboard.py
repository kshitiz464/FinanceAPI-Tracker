"""
Dashboard endpoint tests with RBAC enforcement.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Transaction
from datetime import date, timedelta


class DashboardTestBase(TestCase):
    """Base class for dashboard tests."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin', password='Admin@123', role='admin'
        )
        self.analyst = User.objects.create_user(
            username='analyst', password='Analyst@123', role='analyst'
        )
        self.viewer = User.objects.create_user(
            username='viewer', password='Viewer@123', role='viewer'
        )

        # Create test transactions
        today = date.today()
        Transaction.objects.bulk_create([
            Transaction(amount=5000, type='income', category='Salary',
                        date=today, created_by=self.admin),
            Transaction(amount=3000, type='income', category='Freelance',
                        date=today - timedelta(days=15), created_by=self.admin),
            Transaction(amount=1000, type='expense', category='Groceries',
                        date=today, created_by=self.admin),
            Transaction(amount=2000, type='expense', category='Rent',
                        date=today - timedelta(days=10), created_by=self.admin),
            Transaction(amount=500, type='expense', category='Groceries',
                        date=today - timedelta(days=5), created_by=self.admin,
                        is_deleted=True),  # Soft-deleted, should be excluded
        ])

    def _login(self, username, password):
        response = self.client.post('/api/auth/token/', {
            'username': username, 'password': password,
        })
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
        )


class SummaryTests(DashboardTestBase):
    """Tests for GET /api/dashboard/summary/"""

    def test_summary_returns_correct_totals(self):
        """Summary should correctly calculate income, expenses, and net."""
        self._login('analyst', 'Analyst@123')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], 8000)
        self.assertEqual(response.data['total_expenses'], 3000)
        self.assertEqual(response.data['net_balance'], 5000)

    def test_summary_excludes_soft_deleted(self):
        """Soft-deleted records should NOT be included in summary."""
        self._login('analyst', 'Analyst@123')
        response = self.client.get('/api/dashboard/summary/')
        # Expense total is 3000, not 3500 (soft-deleted 500 excluded)
        self.assertEqual(response.data['total_expenses'], 3000)

    def test_admin_can_access_summary(self):
        """Admin should be able to access summary."""
        self._login('admin', 'Admin@123')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardRBACTests(DashboardTestBase):
    """Test role-based access on dashboard endpoints."""

    def test_viewer_cannot_access_summary(self):
        """Viewer should get 403 on dashboard endpoints."""
        self._login('viewer', 'Viewer@123')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_access_categories(self):
        self._login('viewer', 'Viewer@123')
        response = self.client.get('/api/dashboard/categories/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_access_trends(self):
        self._login('viewer', 'Viewer@123')
        response = self.client.get('/api/dashboard/trends/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        """Unauthenticated user should get 401."""
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_analyst_can_access_categories(self):
        """Analyst should access category breakdown."""
        self._login('analyst', 'Analyst@123')
        response = self.client.get('/api/dashboard/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analyst_can_access_trends(self):
        """Analyst should access monthly trends."""
        self._login('analyst', 'Analyst@123')
        response = self.client.get('/api/dashboard/trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RecentActivityTests(DashboardTestBase):
    """Tests for GET /api/dashboard/recent/"""

    def test_recent_activity(self):
        """Should return recent transactions."""
        self._login('analyst', 'Analyst@123')
        response = self.client.get('/api/dashboard/recent/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_recent_with_limit(self):
        """Limit parameter should cap results."""
        self._login('admin', 'Admin@123')
        response = self.client.get('/api/dashboard/recent/?limit=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 2)


class TopCategoriesTests(DashboardTestBase):
    """Tests for GET /api/dashboard/top-categories/"""

    def test_top_categories(self):
        """Should return top categories for income and expense."""
        self._login('analyst', 'Analyst@123')
        response = self.client.get('/api/dashboard/top-categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('top_income_categories', response.data)
        self.assertIn('top_expense_categories', response.data)

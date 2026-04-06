"""
Transaction CRUD tests with RBAC enforcement.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Transaction
from datetime import date, timedelta


class TransactionTestBase(TestCase):
    """Base class with shared setup for transaction tests."""

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
        self.transaction_data = {
            'amount': 5000.00,
            'type': 'income',
            'category': 'Salary',
            'date': str(date.today()),
            'description': 'Monthly salary',
        }
        # Create a test transaction
        self.transaction = Transaction.objects.create(
            amount=1000, type='expense', category='Groceries',
            date=date.today(), created_by=self.admin,
        )

    def _login(self, user):
        """Helper to authenticate a user for API requests."""
        self.client.force_authenticate(user=user)


class TransactionCRUDTests(TransactionTestBase):
    """Test basic CRUD operations."""

    def test_admin_can_create_transaction(self):
        """Admin should be able to create a transaction."""
        self._login(self.admin)
        response = self.client.post(
            '/api/transactions/', self.transaction_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], 5000.00)
        self.assertEqual(response.data['category'], 'Salary')

    def test_admin_can_update_transaction(self):
        """Admin should be able to update a transaction."""
        self._login(self.admin)
        response = self.client.patch(
            f'/api/transactions/{self.transaction.id}/',
            {'amount': 2000}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_soft_delete(self):
        """DELETE should soft-delete (is_deleted=True), not remove."""
        self._login(self.admin)
        response = self.client.delete(
            f'/api/transactions/{self.transaction.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Record still exists in DB
        self.transaction.refresh_from_db()
        self.assertTrue(self.transaction.is_deleted)

    def test_soft_deleted_not_in_list(self):
        """Soft-deleted transactions should NOT appear in list."""
        self._login(self.admin)
        self.transaction.is_deleted = True
        self.transaction.save()
        response = self.client.get('/api/transactions/')
        ids = [t['id'] for t in response.data['results']]
        self.assertNotIn(self.transaction.id, ids)

    def test_list_transactions(self):
        """Any authenticated user should be able to list transactions."""
        self._login(self.viewer)
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)  # Pagination

    def test_retrieve_single_transaction(self):
        """Any authenticated user should be able to retrieve one transaction."""
        self._login(self.viewer)
        response = self.client.get(
            f'/api/transactions/{self.transaction.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.transaction.id)


class TransactionRBACTests(TransactionTestBase):
    """Test role-based access control enforcement."""

    def test_viewer_cannot_create(self):
        """Viewer should get 403 when trying to create."""
        self._login(self.viewer)
        response = self.client.post(
            '/api/transactions/', self.transaction_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_cannot_create(self):
        """Analyst should get 403 when trying to create."""
        self._login(self.analyst)
        response = self.client.post(
            '/api/transactions/', self.transaction_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_delete(self):
        """Viewer should get 403 when trying to delete."""
        self._login(self.viewer)
        response = self.client.delete(
            f'/api/transactions/{self.transaction.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        """Unauthenticated user should get 401."""
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TransactionFilterTests(TransactionTestBase):
    """Test filtering and search functionality."""

    def setUp(self):
        super().setUp()
        # Create varied transactions for filtering
        Transaction.objects.create(
            amount=500, type='income', category='Freelance',
            date=date.today() - timedelta(days=10), created_by=self.admin,
            description='Web development project',
        )
        Transaction.objects.create(
            amount=200, type='expense', category='Dining',
            date=date.today() - timedelta(days=5), created_by=self.admin,
            description='Team lunch',
        )

    def test_filter_by_type(self):
        """Filter by income/expense type."""
        self._login(self.viewer)
        response = self.client.get('/api/transactions/?type=income')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for t in response.data['results']:
            self.assertEqual(t['type'], 'income')

    def test_filter_by_category(self):
        """Filter by category (case-insensitive)."""
        self._login(self.viewer)
        response = self.client.get('/api/transactions/?category=freelance')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_date_range(self):
        """Filter by date range."""
        self._login(self.viewer)
        date_from = str(date.today() - timedelta(days=7))
        response = self.client.get(f'/api/transactions/?date_from={date_from}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search(self):
        """Search by description/category."""
        self._login(self.viewer)
        response = self.client.get('/api/transactions/?search=lunch')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TransactionValidationTests(TransactionTestBase):
    """Test input validation."""

    def test_negative_amount_rejected(self):
        """Negative amounts should be rejected."""
        self._login(self.admin)
        data = {**self.transaction_data, 'amount': -100}
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_future_date_rejected(self):
        """Future dates should be rejected."""
        self._login(self.admin)
        future = str(date.today() + timedelta(days=30))
        data = {**self.transaction_data, 'date': future}
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_rejected(self):
        """Invalid transaction type should be rejected."""
        self._login(self.admin)
        data = {**self.transaction_data, 'type': 'donation'}
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

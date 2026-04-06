"""
API Root / Welcome view — serves as the homepage at localhost:8000/
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class APIRootView(APIView):
    """
    Welcome to the Finance Dashboard API!
    Lists all available endpoints and their descriptions.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        base_url = request.build_absolute_uri('/api/')
        return Response({
            'message': 'Welcome to the Finance Dashboard API',
            'version': '1.0.0',
            'description': (
                'A secure backend API for finance data processing and access control. '
                'Supports role-based access (admin, analyst, viewer), '
                'financial transaction CRUD, and dashboard analytics.'
            ),
            'endpoints': {
                'auth': {
                    'register': f'{base_url}auth/register/',
                    'login (get tokens)': f'{base_url}auth/token/',
                    'refresh token': f'{base_url}auth/token/refresh/',
                },
                'transactions': {
                    'list & create': f'{base_url}transactions/',
                    'detail (GET/PUT/PATCH/DELETE)': f'{base_url}transactions/{{id}}/',
                },
                'dashboard': {
                    'summary': f'{base_url}dashboard/summary/',
                    'category breakdown': f'{base_url}dashboard/categories/',
                    'monthly trends': f'{base_url}dashboard/trends/',
                    'recent activity': f'{base_url}dashboard/recent/',
                    'top categories': f'{base_url}dashboard/top-categories/',
                },
                'users (admin only)': {
                    'list users': f'{base_url}users/',
                    'user detail': f'{base_url}users/{{id}}/',
                },
                'documentation': {
                    'swagger_ui': request.build_absolute_uri('/api/docs/'),
                    'redoc': request.build_absolute_uri('/api/redoc/'),
                    'schema (OpenAPI)': request.build_absolute_uri('/api/schema/'),
                },
            },
            'admin_panel': request.build_absolute_uri('/admin/'),
            'roles': {
                'viewer': 'Can only view dashboard data and transaction records',
                'analyst': 'Can view records and access analytics/insights',
                'admin': 'Full access — create, update, delete records and manage users',
            },
        })

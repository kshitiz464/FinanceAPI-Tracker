from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)
from api.views.auth_views import RegisterView
from api.views.transaction_views import TransactionViewSet
from api.views.dashboard_views import (
    SummaryView, CategoryBreakdownView, MonthlyTrendsView,
    RecentActivityView, TopCategoriesView,
)
from api.views.user_views import UserListView, UserDetailView

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Transactions (CRUD via router)
    path('', include(router.urls)),

    # Dashboard analytics
    path('dashboard/summary/', SummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/categories/', CategoryBreakdownView.as_view(), name='dashboard-categories'),
    path('dashboard/trends/', MonthlyTrendsView.as_view(), name='dashboard-trends'),
    path('dashboard/recent/', RecentActivityView.as_view(), name='dashboard-recent'),
    path('dashboard/top-categories/', TopCategoriesView.as_view(), name='dashboard-top-categories'),

    # User management (admin only)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]

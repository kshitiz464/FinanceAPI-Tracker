"""
Dashboard analytics views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from api.permissions import IsAnalystOrAdmin
from api.services.dashboard_service import DashboardService
from drf_spectacular.utils import extend_schema


class SummaryView(APIView):
    """Overall financial summary: total income, expenses, net balance."""
    permission_classes = [IsAnalystOrAdmin]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        return Response(DashboardService.get_summary())


class CategoryBreakdownView(APIView):
    """Breakdown of totals by category and type."""
    permission_classes = [IsAnalystOrAdmin]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        return Response(DashboardService.get_category_breakdown())


class MonthlyTrendsView(APIView):
    """Monthly income/expense trends."""
    permission_classes = [IsAnalystOrAdmin]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        return Response(DashboardService.get_monthly_trends())


class RecentActivityView(APIView):
    """Most recent transactions."""
    permission_classes = [IsAnalystOrAdmin]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)  # Cap at 50
        return Response(DashboardService.get_recent_activity(limit=limit))


class TopCategoriesView(APIView):
    """Top categories by income and expense."""
    permission_classes = [IsAnalystOrAdmin]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        limit = int(request.query_params.get('limit', 5))
        limit = min(limit, 20)
        return Response(DashboardService.get_top_categories(limit=limit))

from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDate
from api.models import Transaction


class DashboardService:
    """Business logic for dashboard analytics."""

    @staticmethod
    def get_summary():
        """Overall financial summary: income, expenses, net balance, counts."""
        qs = Transaction.objects.filter(is_deleted=False)
        total_income = qs.filter(type='income').aggregate(
            total=Sum('amount'))['total'] or 0
        total_expense = qs.filter(type='expense').aggregate(
            total=Sum('amount'))['total'] or 0
        return {
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expense, 2),
            'net_balance': round(total_income - total_expense, 2),
            'total_transactions': qs.count(),
            'income_count': qs.filter(type='income').count(),
            'expense_count': qs.filter(type='expense').count(),
        }

    @staticmethod
    def get_category_breakdown():
        """Breakdown of total amounts and counts per category and type."""
        return list(
            Transaction.objects.filter(is_deleted=False)
            .values('category', 'type')
            .annotate(
                total=Sum('amount'),
                count=Count('id'),
                avg_amount=Avg('amount'),
            )
            .order_by('-total')
        )

    @staticmethod
    def get_monthly_trends():
        """Monthly income/expense trends."""
        return list(
            Transaction.objects.filter(is_deleted=False)
            .annotate(month=TruncMonth('date'))
            .values('month', 'type')
            .annotate(
                total=Sum('amount'),
                count=Count('id'),
                avg_amount=Avg('amount'),
            )
            .order_by('month')
        )

    @staticmethod
    def get_recent_activity(limit=10):
        """Most recent transactions."""
        return list(
            Transaction.objects.filter(is_deleted=False)
            .select_related('created_by')
            .order_by('-created_at')[:limit]
            .values(
                'id', 'amount', 'type', 'category', 'date',
                'description', 'created_at', 'created_by__username',
            )
        )

    @staticmethod
    def get_top_categories(limit=5):
        """Top categories by total spending/income."""
        income_top = list(
            Transaction.objects.filter(is_deleted=False, type='income')
            .values('category')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')[:limit]
        )
        expense_top = list(
            Transaction.objects.filter(is_deleted=False, type='expense')
            .values('category')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')[:limit]
        )
        return {
            'top_income_categories': income_top,
            'top_expense_categories': expense_top,
        }

    @staticmethod
    def get_daily_trends(days=30):
        """Daily trends for the last N days."""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now().date() - timedelta(days=days)
        return list(
            Transaction.objects.filter(is_deleted=False, date__gte=cutoff)
            .annotate(day=TruncDate('date'))
            .values('day', 'type')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('day')
        )

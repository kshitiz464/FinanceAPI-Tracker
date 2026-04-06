from api.models import Transaction
from django.db.models import Q


class TransactionService:
    """Business logic for transaction queries."""

    @staticmethod
    def get_filtered_queryset(params):
        """
        Filter transactions based on query parameters.
        Supports: type, category, date_from, date_to, search
        """
        qs = Transaction.objects.filter(is_deleted=False)

        if params.get('type'):
            qs = qs.filter(type=params['type'])
        if params.get('category'):
            qs = qs.filter(category__icontains=params['category'])
        if params.get('date_from'):
            qs = qs.filter(date__gte=params['date_from'])
        if params.get('date_to'):
            qs = qs.filter(date__lte=params['date_to'])

        # Search support — searches description and category
        search = params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )

        return qs

    @staticmethod
    def soft_delete(transaction):
        """Soft delete a transaction (sets is_deleted=True)."""
        transaction.is_deleted = True
        transaction.save(update_fields=['is_deleted', 'updated_at'])
        return transaction

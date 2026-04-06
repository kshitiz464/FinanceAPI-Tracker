from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models import Transaction
from api.serializers import TransactionSerializer, TransactionCreateSerializer
from api.permissions import IsAdmin, IsAnalystOrAdmin, IsAnyAuthenticatedRole
from api.services.transaction_service import TransactionService

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdmin()]
        if self.action in ('list', 'retrieve'):
            return [IsAnyAuthenticatedRole()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TransactionCreateSerializer
        return TransactionSerializer

    def get_queryset(self):
        params = self.request.query_params
        return TransactionService.get_filtered_queryset(params)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        TransactionService.soft_delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

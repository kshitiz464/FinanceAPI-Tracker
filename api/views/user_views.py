"""
User management views — admin only.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from api.models import User
from api.serializers import UserResponseSerializer, UserUpdateSerializer
from api.permissions import IsAdmin


class UserListView(generics.ListAPIView):
    """List all users. Admin only."""
    serializer_class = UserResponseSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all().order_by('-date_joined')


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a user (role, is_active status).
    Admin only.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserResponseSerializer
        return UserUpdateSerializer

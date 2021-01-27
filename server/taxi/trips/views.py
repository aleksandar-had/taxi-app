from django.contrib.auth import get_user_model
from rest_framework import generics

from .serializers import UserSerializer


# Extend Django REST Framework’s CreateAPIView and leverage on
# UserSerializer to create a new user.
class SignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

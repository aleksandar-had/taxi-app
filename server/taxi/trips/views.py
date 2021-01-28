from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, LogInSerializer


# Extend Django REST Framework’s CreateAPIView and leverage on
# UserSerializer to create a new user.
class SignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class LogInView(TokenObtainPairView):
    serializer_class = LogInSerializer
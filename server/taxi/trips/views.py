from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Trip
from .serializers import UserSerializer, LogInSerializer, TripSerializer


# Extend Django REST Framework’s CreateAPIView and leverage on
# UserSerializer to create a new user.
class SignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class LogInView(TokenObtainPairView):
    serializer_class = LogInSerializer


class TripView(viewsets.ReadOnlyModelViewSet):
    # tells the view to get the trip record by its id value
    lookup_field = "id"

    # tells the view what named parameter to use to extract
    # the id value from the URL
    lookup_url_kwarg = "trip_id"

    permission_classes = (permissions.IsAuthenticated,)
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

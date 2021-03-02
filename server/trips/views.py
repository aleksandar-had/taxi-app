from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Trip
from .serializers import UserSerializer, LogInSerializer, TripSerializer, NestedTripSerializer


# Extend Django REST Framework’s CreateAPIView and leverage on
# UserSerializer to create a new user.
class SignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class LogInView(TokenObtainPairView):
    serializer_class = LogInSerializer


class TripView(viewsets.ReadOnlyModelViewSet):
    # Tells the view to get the trip record by its id value
    lookup_field = "id"
    # Tells the view what named parameter to use to extract
    # the id value from the URL
    lookup_url_kwarg = "trip_id"

    permission_classes = (permissions.IsAuthenticated,)
    # Use NestedTripSerializer to include the full layer of user (rider/driver) info
    serializer_class = NestedTripSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.group == "driver":
            return Trip.objects.filter(
                Q(status=Trip.REQUESTED) | Q(driver=user)
            )
        if user.group == "rider":
            return Trip.objects.filter(rider=user)
        return Trip.objects.none()

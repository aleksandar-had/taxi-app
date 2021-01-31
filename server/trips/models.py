import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse


# If you’re starting a new project, it’s highly recommended to set up a custom
# user model, even if the default User model is sufficient for you. This model
# behaves identically to the default user model, but you’ll be able to
# customize it in the future if the need arises.
class User(AbstractUser):
    pass


class Trip(models.Model):
    REQUESTED = "REQUESTED"
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    STATUSES = (
        (REQUESTED, REQUESTED),
        (STARTED, STARTED),
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    pick_up_address = models.CharField(max_length=255)
    drop_off_address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUSES, default=REQUESTED)

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return reverse("trip:trip_detail", kwargs={"trip_id": self.id})
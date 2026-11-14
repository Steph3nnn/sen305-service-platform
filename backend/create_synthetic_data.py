
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from requests_app.models import Category, ServiceRequest

User = get_user_model()

user, created = User.objects.get_or_create(
    username="synthetic_lab_user",
    defaults={"email": "synthetic@example.com"},
)

if created:
    user.set_unusable_password()
    user.save()

network, _ = Category.objects.get_or_create(
    name="SYNTHETIC Network Support",
    defaults={"description": "Synthetic network laboratory data"},
)

hardware, _ = Category.objects.get_or_create(
    name="SYNTHETIC Hardware Support",
    defaults={"description": "Synthetic hardware laboratory data"},
)

categories = [network, hardware]

statuses = [
    ServiceRequest.Status.OPEN,
    ServiceRequest.Status.ASSIGNED,
    ServiceRequest.Status.IN_PROGRESS,
]

now = timezone.now()

for i in range(12):
    ServiceRequest.objects.get_or_create(
        title=f"Synthetic Laboratory Request {i + 1}",
        defaults={
            "requester": user,
            "category": categories[i % 2],
            "description": "Artificial data for database query analysis.",
            "location": "Synthetic Testing Laboratory",
            "priority": (i % 5) + 1,
            "status": statuses[i % 3],
            "due_at": now + timedelta(days=i - 5),
        },
    )

print("Synthetic categories:", Category.objects.filter(
    name__startswith="SYNTHETIC"
).count())

print("Synthetic requests:", ServiceRequest.objects.filter(
    title__startswith="Synthetic Laboratory Request"
).count())

print("Synthetic data creation complete.")

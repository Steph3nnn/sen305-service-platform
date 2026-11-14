
from requests_app.models import Category, ServiceRequest

network = Category.objects.get(name="SYNTHETIC Network Support")

queryset = ServiceRequest.objects.filter(
    category=network,
    status__in=[
        ServiceRequest.Status.OPEN,
        ServiceRequest.Status.ASSIGNED,
    ],
    title__startswith="Synthetic Laboratory Request",
).order_by("priority", "created_at")

print("\n--- QUERY RESULTS ---")
for request in queryset:
    print(request.title, request.priority, request.status, request.created_at)

print("\n--- GENERATED SQL ---")
print(queryset.query)

print("\n--- MYSQL EXECUTION PLAN ---")
print(queryset.explain())

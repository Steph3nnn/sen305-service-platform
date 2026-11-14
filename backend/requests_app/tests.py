
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Category, ServiceRequest


class ServiceRequestValidationTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="synthetic_tester",
            password="test-password-123",
        )

        self.category = Category.objects.create(
            name="Laboratory Equipment",
            description="Synthetic test category",
        )

    def create_request(self, **kwargs):
        data = {
            "requester": self.user,
            "category": self.category,
            "title": "Synthetic equipment request",
            "description": "Laboratory testing only",
            "location": "Test Laboratory",
            "status": ServiceRequest.Status.OPEN,
        }

        data.update(kwargs)

        return ServiceRequest(**data)

    def test_resolved_request_requires_resolved_at(self):
        request = self.create_request(
            status=ServiceRequest.Status.RESOLVED,
            resolution_summary="Equipment repaired",
        )

        with self.assertRaises(ValidationError) as error:
            request.full_clean()

        self.assertIn("resolved_at", error.exception.message_dict)

    def test_resolved_request_requires_summary(self):
        request = self.create_request(
            status=ServiceRequest.Status.RESOLVED,
            resolved_at=timezone.now(),
        )

        with self.assertRaises(ValidationError) as error:
            request.full_clean()

        self.assertIn(
            "resolution_summary",
            error.exception.message_dict,
        )

    def test_closed_request_requires_both_fields(self):
        request = self.create_request(
            status=ServiceRequest.Status.CLOSED,
        )

        with self.assertRaises(ValidationError) as error:
            request.full_clean()

        self.assertIn("resolved_at", error.exception.message_dict)
        self.assertIn(
            "resolution_summary",
            error.exception.message_dict,
        )

    def test_valid_resolved_request_passes_validation(self):
        request = self.create_request(
            status=ServiceRequest.Status.RESOLVED,
            resolved_at=timezone.now(),
            resolution_summary="The equipment was successfully repaired.",
        )

        request.full_clean()

    def test_open_request_does_not_require_resolution_details(self):
        request = self.create_request(
            status=ServiceRequest.Status.OPEN,
        )

        request.full_clean()


class ServiceRequestDueDateTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="due_date_tester",
            password="test-password-123",
        )

        self.category = Category.objects.create(
            name="Synthetic Network Testing",
            description="Synthetic network requests",
        )

    def test_filter_requests_by_due_date(self):
        chosen_time = timezone.now()

        overdue = ServiceRequest.objects.create(
            requester=self.user,
            category=self.category,
            title="Synthetic request due earlier",
            description="Laboratory test",
            location="Test Lab",
            due_at=chosen_time - timedelta(hours=2),
        )

        upcoming = ServiceRequest.objects.create(
            requester=self.user,
            category=self.category,
            title="Synthetic request due later",
            description="Laboratory test",
            location="Test Lab",
            due_at=chosen_time + timedelta(hours=2),
        )

        results = ServiceRequest.objects.filter(
            due_at__lt=chosen_time
        )

        self.assertIn(overdue, results)
        self.assertNotIn(upcoming, results)

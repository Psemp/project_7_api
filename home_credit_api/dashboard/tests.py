from django.test import TestCase
from django.urls import reverse


class DashboardViewTestCase(TestCase):
    def test_dashboard_view(self):
        url = reverse("dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/dashboard.html")
        self.assertIn("is_dashboard", response.context)
        self.assertTrue(response.context["is_dashboard"])

from django.test import TestCase
from events.models import Event
from rest_framework.test import APITestCase, APIClient

class EventBriteTest(APITestCase, TestCase):
    client = APIClient()

    def setUp(self):
        Event.objects.create(eventbrite_event_id='89893504893')

    def test_can_check_registration_by_email(self):
        response = self.client.post('/apps/cms/api/events/check?email=mwharrison@rice.edu', follow=True)
        self.assertEqual(response.content.decode("utf-8"), '{"registered": true}')

    def test_returns_false_if_not_registered(self):
        response = self.client.post('/apps/cms/api/events/check?email=not_registered@openstax.org', follow=True)
        self.assertEqual(response.content.decode("utf-8"), '{"registered": false}')

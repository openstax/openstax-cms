from django.utils import timezone
from django.test import TestCase
from events.models import Event, Session
from rest_framework.test import APITestCase, APIClient, APIRequestFactory

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


class SessionTest(APITestCase, TestCase):
    client = APIClient()

    def setUp(self):
        self.event = Event.objects.create(eventbrite_event_id='89893504893')

    def test_can_create_session(self):
        session = Session.objects.create(event=self.event,
                                         name='Making OER',
                                         date=timezone.now(),
                                         location='BRC',
                                         seats_remaining=15)
        self.assertEqual(session.name, 'Making OER')
        self.assertGreater(Session.objects.all().count(), 0)

    def test_session_api_endpoint(self):
        session = Session.objects.create(event=self.event,
                                         name='Doing OER Right',
                                         date=timezone.now(),
                                         location='Rice Memorial Center',
                                         seats_remaining=15)

        response = self.client.post('/apps/cms/api/events/sessions', follow=True)
        self.assertContains(response, 'Doing OER Right')


class RegistrationTest(APITestCase, TestCase):
    factory = APIRequestFactory()
    client = APIClient()

    def setUp(self):
        self.event = Event.objects.create(eventbrite_event_id='89893504893')
        self.session = Session.objects.create(event=self.event,
                                         name='Doing OER Right',
                                         date=timezone.now(),
                                         location='Rice Memorial Center',
                                         seats_remaining=15)

    def test_can_register_via_api(self):
        request = self.client.post('/apps/cms/api/events/registration', {'session': self.session.id,
                                                                     'first_name': 'George',
                                                                     'last_name': 'McFly',
                                                                     'registration_email': 'mwharrison@rice.edu'},
                               format='json', follow=True)

        print(response.content.decode("utf-8"))

        response = self.client.get('/apps/cms/api/events/registration', follow=True)
        print(response.status_code)
        print(response)
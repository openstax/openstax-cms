from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from wagtail.models import Locale

from snippets.models import Subject

PREVIEW_URL = '/apps/cms/api/v2/pages/table-block/preview/'


class TablePreviewViewTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user('staff-preview', password='x', is_staff=True)
        self.non_staff = User.objects.create_user('nobody-preview', password='x', is_staff=False)

    def test_anonymous_denied(self):
        response = self.client.post(PREVIEW_URL, {
            'source_type': 'subjects', 'config': {'variant': 'he', 'columns': []},
        }, format='json')
        self.assertIn(response.status_code, (401, 403))

    def test_non_staff_denied(self):
        self.client.force_authenticate(self.non_staff)
        response = self.client.post(PREVIEW_URL, {
            'source_type': 'subjects', 'config': {'variant': 'he', 'columns': []},
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_valid_source_returns_columns_and_rows(self):
        Subject.objects.create(name='Math', locale=Locale.get_default())
        self.client.force_authenticate(self.staff)
        response = self.client.post(PREVIEW_URL, {
            'source_type': 'subjects',
            'config': {'variant': 'he', 'columns': [{'field': 'name', 'header': '', 'type': ''}]},
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['columns'], [{'header': 'Subject', 'type': 'text'}])
        self.assertEqual(response.data['rows'][0]['cells'][0]['content'], 'Math')

    def test_unknown_source_type_returns_error_not_500(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(PREVIEW_URL, {
            'source_type': 'nonsense', 'config': {},
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.data)

    def test_missing_source_type_returns_error(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(PREVIEW_URL, {'config': {}}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.data)

    def test_rows_capped_at_five(self):
        for i in range(8):
            Subject.objects.create(name=f'Subject {i}', locale=Locale.get_default())
        self.client.force_authenticate(self.staff)
        response = self.client.post(PREVIEW_URL, {
            'source_type': 'subjects',
            'config': {'variant': 'he', 'columns': [{'field': 'name', 'header': '', 'type': ''}]},
        }, format='json')
        self.assertEqual(len(response.data['rows']), 5)

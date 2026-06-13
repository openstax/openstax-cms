from unittest import mock

from django.test import TestCase, override_settings

from shared import analytics


class AnalyticsCaptureTest(TestCase):
    def setUp(self):
        analytics._client = None  # reset memoized client between tests
        analytics._client_key = None

    @override_settings(POSTHOG_API_KEY=None)
    @mock.patch('shared.analytics.Posthog')
    def test_capture_is_noop_when_unconfigured(self, mock_posthog):
        analytics.capture('errata_submitted', distinct_id='uuid-1')
        mock_posthog.assert_not_called()

    @override_settings(POSTHOG_API_KEY='phc_test', POSTHOG_HOST='https://z.openstax.org')
    @mock.patch('shared.analytics.Posthog')
    def test_capture_sends_identified_event(self, mock_posthog):
        client = mock_posthog.return_value
        analytics.capture(
            'errata_submitted',
            distinct_id='uuid-1',
            properties={'form_type': 'errata'},
        )
        client.capture.assert_called_once()
        kwargs = client.capture.call_args.kwargs
        self.assertEqual(kwargs['distinct_id'], 'uuid-1')
        self.assertEqual(kwargs['event'], 'errata_submitted')
        self.assertEqual(kwargs['properties']['form_type'], 'errata')
        self.assertEqual(kwargs['properties']['source'], 'server')

    @override_settings(POSTHOG_API_KEY='phc_test')
    @mock.patch('shared.analytics.Posthog')
    def test_capture_anonymous_disables_person_profile(self, mock_posthog):
        client = mock_posthog.return_value
        analytics.capture('thank_you_note_submitted')
        kwargs = client.capture.call_args.kwargs
        self.assertTrue(kwargs['properties']['$process_person_profile'] is False)
        self.assertTrue(kwargs['distinct_id'])  # a generated id, not empty

    @override_settings(POSTHOG_API_KEY='phc_test')
    @mock.patch('shared.analytics.Posthog')
    def test_capture_swallows_sdk_errors(self, mock_posthog):
        mock_posthog.return_value.capture.side_effect = RuntimeError('boom')
        analytics.capture('errata_submitted', distinct_id='uuid-1')  # must not raise

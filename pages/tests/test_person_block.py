from django.test import TestCase
from pages.models import PersonTag


class PersonTagModelTests(TestCase):
    def test_str_is_name(self):
        tag = PersonTag.objects.create(name="Core Team", slug="core-team")
        self.assertEqual(str(tag), "Core Team")

    def test_default_ordering_by_sort_order_then_name(self):
        PersonTag.objects.create(name="Zeta", slug="zeta", sort_order=1)
        PersonTag.objects.create(name="Alpha", slug="alpha", sort_order=2)
        PersonTag.objects.create(name="Beta", slug="beta", sort_order=1)
        self.assertEqual(
            [t.name for t in PersonTag.objects.all()],
            ["Beta", "Zeta", "Alpha"],
        )

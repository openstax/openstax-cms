from django.test import TestCase
from pages.models import PersonTag
from pages.custom_blocks import PersonTagChooserBlock, PersonBlock
from pages.models.constants import BASE_CONTENT_BLOCKS


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


class PersonTagChooserBlockTests(TestCase):
    def test_get_api_representation_emits_id_name_slug(self):
        tag = PersonTag.objects.create(name="Core Team", slug="core-team")
        block = PersonTagChooserBlock(PersonTag)
        self.assertEqual(
            block.get_api_representation(tag),
            {"id": tag.id, "name": "Core Team", "slug": "core-team"},
        )

    def test_get_api_representation_none_for_empty(self):
        block = PersonTagChooserBlock(PersonTag)
        self.assertIsNone(block.get_api_representation(None))


class PersonBlockTests(TestCase):
    def _person(self, **overrides):
        data = {
            "name": "Ada Lovelace",
            "title": "Mathematician",
            "image": None,
            "short_bio": "Pioneer of computing.",
            "full_bio": "",
            "links": [],
            "tags": [],
        }
        data.update(overrides)
        return data

    def test_minimal_person_serializes_optional_fields_empty(self):
        block = PersonBlock()
        value = block.to_python({
            "heading": "",
            "people": [self._person()],
            "config": [],
        })
        rep = block.get_api_representation(value)
        person = rep["people"][0]
        self.assertEqual(person["name"], "Ada Lovelace")
        self.assertEqual(person["full_bio"], "")
        self.assertEqual(person["links"], [])
        self.assertEqual(person["tags"], [])

    def test_links_serialize_type_and_url(self):
        block = PersonBlock()
        value = block.to_python({
            "heading": "",
            "people": [self._person(links=[
                {"type": "linkedin", "url": "https://linkedin.com/in/ada"},
            ])],
            "config": [],
        })
        rep = block.get_api_representation(value)
        self.assertEqual(
            rep["people"][0]["links"][0],
            {"type": "linkedin", "url": "https://linkedin.com/in/ada"},
        )

    def test_tags_serialize_inline(self):
        tag = PersonTag.objects.create(name="Core Team", slug="core-team")
        block = PersonBlock()
        value = block.to_python({
            "heading": "Our Team",
            "people": [self._person(tags=[tag.id])],
            "config": [],
        })
        rep = block.get_api_representation(value)
        self.assertEqual(
            rep["people"][0]["tags"][0],
            {"id": tag.id, "name": "Core Team", "slug": "core-team"},
        )


class PersonBlockRegistrationTests(TestCase):
    def test_person_is_a_base_content_block(self):
        keys = [name for name, _ in BASE_CONTENT_BLOCKS]
        self.assertIn("person", keys)

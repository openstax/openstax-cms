from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from pages import models as page_models
from shared.test_utilities import mock_user_login


class TemplateTagTests(WagtailPageTestCase):
    """Test cases for custom template tags in pages app"""

    def setUp(self):
        """Set up test data"""
        mock_user_login()
        
        # Get root page
        root_page = Page.objects.get(title="Root")
        
        # Create a test page with various field types
        self.test_page = page_models.HomePage(
            title="Test HomePage",
            slug="test-home",
            banner_headline="Test Headline",
            banner_description="Test description text",
            features_headline="Features Test",
        )
        root_page.add_child(instance=self.test_page)

    def test_get_page_content_extracts_char_field(self):
        """Test that get_page_content extracts CharField values"""
        from django.template import Context, Template
        
        template = Template('{% load pages_tags %}{% get_page_content page as content %}{{ content|length }}')
        context = Context({'page': self.test_page})
        result = template.render(context)
        
        # Should extract multiple fields
        self.assertGreater(int(result), 0)
        
        # Test actual content extraction
        template = Template('{% load pages_tags %}{% get_page_content page as content %}{% for item in content %}{{ item.name }}:{{ item.value }}|{% endfor %}')
        context = Context({'page': self.test_page})
        result = template.render(context)
        
        # Should contain our test data
        self.assertIn('banner_headline:Test Headline', result)
        self.assertIn('banner_description:Test description text', result)

    def test_get_page_content_extracts_text_field(self):
        """Test that get_page_content extracts TextField values"""
        from django.template import Context, Template
        
        template = Template('{% load pages_tags %}{% get_page_content page as content %}{% for item in content %}{% if item.name == "banner_description" %}{{ item.value }}{% endif %}{% endfor %}')
        context = Context({'page': self.test_page})
        result = template.render(context)
        
        self.assertEqual(result.strip(), 'Test description text')

    def test_get_page_content_extracts_stream_field(self):
        """Test that get_page_content extracts StreamField values"""
        from django.template import Context, Template
        
        # Update the test page with StreamField data
        self.test_page.features_tab1_features = [
            ('feature_text', 'Feature One'),
            ('feature_text', 'Feature Two'),
        ]
        self.test_page.save()
        
        template = Template('{% load pages_tags %}{% get_page_content page as content %}{% for item in content %}{% if item.name == "features_tab1_features" %}{{ item.value }}{% endif %}{% endfor %}')
        context = Context({'page': self.test_page})
        result = template.render(context)
        
        # Should contain the StreamField content
        self.assertIn('Feature One', result)
        self.assertIn('Feature Two', result)

    def test_get_page_content_filters_system_fields(self):
        """Test that get_page_content filters out internal/system fields"""
        from django.template import Context, Template
        
        template = Template('{% load pages_tags %}{% get_page_content page as content %}{% for item in content %}{{ item.name }}|{% endfor %}')
        context = Context({'page': self.test_page})
        result = template.render(context)
        
        # Should NOT contain system fields
        self.assertNotIn('id|', result)
        self.assertNotIn('path|', result)
        self.assertNotIn('depth|', result)
        self.assertNotIn('slug|', result)
        self.assertNotIn('seo_title|', result)
        self.assertNotIn('content_type|', result)

    def test_get_page_content_handles_none_values(self):
        """Test that get_page_content handles None values gracefully"""
        from django.template import Context, Template
        
        # Create a page with minimal data
        root_page = Page.objects.get(title="Root")
        minimal_page = page_models.HomePage(
            title="Minimal Page",
            slug="minimal",
        )
        root_page.add_child(instance=minimal_page)
        
        template = Template('{% load pages_tags %}{% get_page_content page as content %}{{ content|length }}')
        context = Context({'page': minimal_page})
        result = template.render(context)
        
        # Should not crash and should return a number
        result_int = int(result)
        self.assertGreaterEqual(result_int, 0)

    def test_get_page_content_handles_empty_values(self):
        """Test that get_page_content filters out empty values"""
        from django.template import Context, Template
        from pages.templatetags.pages_tags import get_page_content
        
        # Get content directly using the template tag function
        context = Context({'page': self.test_page})
        content = get_page_content(context, self.test_page)
        
        # All returned items should have non-empty values
        for item in content:
            self.assertIn('name', item, "Item missing 'name' key")
            self.assertIn('value', item, "Item missing 'value' key")
            self.assertTrue(item.get('value', '').strip(), 
                          f"Item {item.get('name', 'unknown')} has empty value")

    def test_get_page_content_with_none_page(self):
        """Test that get_page_content handles None page gracefully"""
        from django.template import Context, Template
        
        template = Template('{% load pages_tags %}{% get_page_content page as content %}{{ content|length }}')
        context = Context({'page': None})
        result = template.render(context)
        
        self.assertEqual(result.strip(), '0')

    def test_extract_content_handles_primitives(self):
        """Test that extract_content handles primitive types"""
        from pages.templatetags.pages_tags import extract_content
        
        self.assertEqual(extract_content("test string"), "test string")
        self.assertEqual(extract_content(123), "123")
        self.assertEqual(extract_content(45.67), "45.67")
        self.assertEqual(extract_content(None), "")

    def test_extract_content_handles_richtext(self):
        """Test that extract_content handles RichText objects"""
        from pages.templatetags.pages_tags import extract_content
        from wagtail.rich_text import RichText
        
        rich = RichText("<p>Rich text content</p>")
        result = extract_content(rich)
        
        self.assertIn("Rich text content", result)

    def test_extract_content_handles_lists(self):
        """Test that extract_content handles list values"""
        from pages.templatetags.pages_tags import extract_content
        
        test_list = ["item1", "item2", "item3"]
        result = extract_content(test_list)
        
        self.assertIn("item1", result)
        self.assertIn("item2", result)
        self.assertIn("item3", result)

    def test_extract_content_handles_nested_structures(self):
        """Test that extract_content recursively extracts from nested structures"""
        from pages.templatetags.pages_tags import extract_content
        
        # Test with nested list
        nested = [["inner1", "inner2"], "outer"]
        result = extract_content(nested)
        
        self.assertIn("inner1", result)
        self.assertIn("inner2", result)
        self.assertIn("outer", result)

    def test_extract_content_handles_dict_like_objects(self):
        """Test that extract_content handles dict-like objects with values() method"""
        from pages.templatetags.pages_tags import extract_content
        
        # Create a mock object with values() method
        class MockStructValue:
            def values(self):
                return ["value1", "value2"]
        
        mock = MockStructValue()
        result = extract_content(mock)
        
        self.assertIn("value1", result)
        self.assertIn("value2", result)

    def test_extract_content_handles_plain_dict(self):
        """Test that extract_content handles plain Python dicts explicitly"""
        from pages.templatetags.pages_tags import extract_content
        
        # Test with a plain dict
        plain_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
        result = extract_content(plain_dict)
        
        # Should extract all values from the dict
        self.assertIn("value1", result)
        self.assertIn("value2", result)
        self.assertIn("value3", result)
        
        # Should not include the keys (we only extract values)
        self.assertNotIn("key1", result)
        self.assertNotIn("key2", result)
        self.assertNotIn("key3", result)

    def test_get_page_content_returns_proper_structure(self):
        """Test that get_page_content returns items with correct structure"""
        from django.template import Context, Template
        from pages.templatetags.pages_tags import get_page_content
        
        # Get content directly to check structure
        context = Context({'page': self.test_page})
        content = get_page_content(context, self.test_page)
        
        # Each item should be a dict with required keys
        for item in content:
            self.assertIsInstance(item, dict, "Content item should be a dictionary")
            self.assertIn('name', item, "Item missing 'name' key")
            self.assertIn('type', item, "Item missing 'type' key")
            self.assertIn('value', item, "Item missing 'value' key")
            self.assertIsInstance(item['name'], str, "Item name should be a string")
            self.assertIsInstance(item['type'], str, "Item type should be a string")
            self.assertIsInstance(item['value'], str, "Item value should be a string")


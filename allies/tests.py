from unittest import TestCase

from allies.models import AllySubject, Ally
from snippets.models import Subject

from wagtail.test.utils import WagtailTestUtils, WagtailPageTestCase


class AlliesTests(WagtailPageTestCase):
    def setUp(self):
        self.math = Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title",
                            search_description="Math page description.")
        self.math.save()

        self.economics = Subject(name="Economics", page_content="Economics page content.",
                                 seo_title="Economics SEO Title",
                                 search_description="Economics page description.")
        self.economics.save()

        self.subject = Subject(name="Science", page_content="Science page content.", seo_title="Science SEO Title",
                          search_description="Science page description.")
        self.subject.save()

        self.ally = Ally(online_homework=True,
                        adaptive_courseware=False,
                        customization_tools=False,
                        is_ap=False,
                        do_not_display=False,
                        heading='Ally Heading',
                        short_description='short description',
                        long_description='long description',
                         slug='new-ally',
                         depth=1,
                         title='Ally Page',
                         path='ally')
        self.ally.save()

    def test_can_create_ally_subject(self):
        ally_subject = AllySubject(subject=self.math, ally=self.ally)
        ally_subject.save()
        result = AllySubject.objects.all()[0]
        self.assertEquals('Math', result.get_subject_name())

    def test_can_create_ally(self):
        result = Ally.objects.all()[0]
        self.assertEquals('Ally Heading', result.heading)

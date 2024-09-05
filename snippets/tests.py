from django.test import TestCase, Client

from snippets import models as snippets_models


class SnippetsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.math = snippets_models.Subject(name="Math", page_content="Math page content.", seo_title="Math SEO Title",
                                            search_description="Math page description.")
        self.math.save()

        self.economics = snippets_models.Subject(name="Economics", page_content="Economics page content.",
                                                 seo_title="Economics SEO Title",
                                                 search_description="Economics page description.")
        self.economics.save()

        self.live = snippets_models.ErrataContent(heading='Errata Content - Live', book_state='live',
                                                  content='All OpenStax textbooks undergo a rigorous review process. '
                                                          'However, like any professional-grade textbook, '
                                                          'errors sometimes occur. The good part is, since our books '
                                                          'are web-based, we can make updates periodically. If you '
                                                          'have a correction to suggest, submit it here. We review '
                                                          'your suggestion and make necessary changes.')
        self.live.save()

        self.deprecated = snippets_models.ErrataContent(heading='Errata Content - Deprecated', book_state='deprecated',
                                                        content='No more corrections will be made')
        self.deprecated.save()

        self.give_banner = snippets_models.GiveBanner(
            html_message="Help students around the world succeed with <strong>contributions of $5, $10 or $20</strong>",
            link_text="Make a difference now", link_url='https://example.com')
        self.give_banner.save()

        self.report = snippets_models.BlogContentType(content_type="Report")
        self.report.save()
        self.video = snippets_models.BlogContentType(content_type="Video")
        self.video.save()
        self.whitepaper = snippets_models.BlogContentType(content_type="Whitepaper")
        self.whitepaper.save()

        self.no_webinar_message = snippets_models.NoWebinarMessage(
            no_webinar_message="No webinars currently scheduled. In the meantime, please watch any of our past "
                               "webinars.")
        self.no_webinar_message.save()

        self.k12subject = snippets_models.K12Subject(name="Test Subject", intro_text='Intro text',
                                                     subject_link="https://example.com/openstaxk12")
        self.k12subject.save()

        self.faculty_resource = snippets_models.FacultyResource(heading="Faculty Resource",
                                                                description='resource description',
                                                                unlocked_resource=True)
        self.faculty_resource.save()

        self.student_resource = snippets_models.StudentResource(heading="Student Resource",
                                                                description='resource description',
                                                                unlocked_resource=True)
        self.student_resource.save()

        self.role = snippets_models.Role(display_name="role display name", salesforce_name='role salesforce name')
        self.role.save()

        self.shared_content = snippets_models.SharedContent(title="shared content", heading='shared content heading',
                                                            content='shared content')
        self.shared_content.save()

        self.news_source = snippets_models.NewsSource(name="news source")
        self.news_source.save()

        self.subject_category = snippets_models.SubjectCategory(subject_category="subject category",
                                                                description='subject category description')
        self.subject_category.save()

        self.blog_collection = snippets_models.BlogCollection(name="blog collection",
                                                              description='blog collection description')
        self.blog_collection.save()

        self.amazon_book_blurb = snippets_models.AmazonBookBlurb(
            amazon_book_blurb="Amazon Book Blurb. Amazon Book Blurb. Amazon Book Blurb.")
        self.amazon_book_blurb.save()

        self.content_warning = snippets_models.ContentWarning(content_warning="Content Warning")
        self.content_warning.save()

    def test_can_create_subject(self):
        subject = snippets_models.Subject(name="Science", page_content="Science page content.",
                                          seo_title="Science SEO Title",
                                          search_description="Science page description.")
        subject.save()

        self.assertEqual(subject.name, "Science")

    def test_can_fetch_all_subjects(self):
        response = self.client.get('/apps/cms/api/snippets/subjects/?format=json')
        self.assertIn(b"Math SEO Title", response.content)
        self.assertIn(b"Economics page description.", response.content)

    def test_can_query_subjects_by_name(self):
        response = self.client.get('/apps/cms/api/snippets/subjects/?name=Math&format=json')
        self.assertIn(b"Math page content.", response.content)

    def test_can_fetch_all_errata_content(self):
        response = self.client.get('/apps/cms/api/snippets/erratacontent/?format=json')
        self.assertIn(b"live", response.content)
        self.assertIn(b"deprecated", response.content)

    def test_can_query_errata_content_by_book_state(self):
        response = self.client.get('/apps/cms/api/snippets/erratacontent/?book_state=deprecated&format=json')
        self.assertIn(b"deprecated", response.content)

    def test_can_fetch_all_give_banners(self):
        response = self.client.get('/apps/cms/api/snippets/givebanner/?format=json')
        self.assertIn(b"Help students", response.content)

    def test_can_fetch_all_blog_content_types(self):
        response = self.client.get('/apps/cms/api/snippets/blogcontenttype/?format=json')
        self.assertIn(b"Whitepaper", response.content)

    def test_can_fetch_no_webinar_message(self):
        response = self.client.get('/apps/cms/api/snippets/nowebinarmessage/?format=json')
        self.assertIn(b"No webinars currently scheduled", response.content)

    def test_can_fetch_k12_subject(self):
        response = self.client.get('/apps/cms/api/snippets/k12subjects/?format=json')
        self.assertIn(b"https://example.com/openstaxk12", response.content)

    def test_can_fetch_faculty_resource(self):
        faculty_resource = snippets_models.FacultyResource.objects.all()[0]
        self.assertEqual(True, faculty_resource.unlocked_resource)

    def test_can_fetch_student_resource(self):
        student_resource = snippets_models.StudentResource.objects.all()[0]
        self.assertEqual(True, student_resource.unlocked_resource)

    def test_can_fetch_role(self):
        response = self.client.get('/apps/cms/api/snippets/roles/?format=json')
        self.assertIn(b"role display name", response.content)

    def test_can_fetch_shared_content(self):
        shared_content = snippets_models.SharedContent.objects.all()[0]
        self.assertEqual('shared content', shared_content.title)

    def test_can_fetch_news_source(self):
        news_source = snippets_models.NewsSource.objects.all()[0]
        self.assertEqual('news source', news_source.name)

    def test_can_fetch_subject_category(self):
        response = self.client.get('/apps/cms/api/snippets/subjectcategory/?format=json')
        self.assertIn(b"subject category description", response.content)

    def test_can_fetch_blog_collection(self):
        response = self.client.get('/apps/cms/api/snippets/blogcollection/?format=json')
        self.assertIn(b"blog collection description", response.content)

    def test_can_fetch_amazon_book_blurb(self):
        response = self.client.get('/apps/cms/api/snippets/amazonbookblurb/?format=json')
        self.assertIn(b"Amazon Book Blurb", response.content)

    def test_can_create_promote_snippet(self):
        promote_snippet = snippets_models.PromoteSnippet(name="Assignable",
                                                         description="Assignable is available on this book.")
        promote_snippet.save()

        self.assertEqual(promote_snippet.name, "Assignable")

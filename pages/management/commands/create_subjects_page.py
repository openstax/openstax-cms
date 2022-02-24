import json
from django.core.management.base import BaseCommand
from pages.models import HomePage, Subjects


class Command(BaseCommand):
    help="Populate subjects page after a deployment"

    def handle(self, *args, **options):
        homepage = HomePage.objects.first() # there's only one home page, so this should be okay
        subjects_page = Subjects(
            title="New Subjects",
            heading="Browse Our Subjects",
            description="North, South, East, West, our subjects are the best!",
            tutor_ad=json.dumps([
                {"type": "content",
                  "value": {'heading': "INSTRUCTORS, TAKE YOUR COURSE ONLINE",
                            'ad_html': "<strong>Assign homework and readings synced with OpenStax textbooks</strong>",
                            'link_text': "Learn more",
                            'link_href': "https://openstax.org/tutor"
                            },
                }
            ]),
            about_os=json.dumps([
                {"type": "content",
                  "value": {'heading': "About Openstax textbooks",
                            'os_text': 'OpenStax is part of Rice University, which is a 501(c)(3) nonprofit charitable corporation. Our mission is to improve educational access and learning for everyone. We do this by publishing openly licensed books, developing and improving research-based courseware, establishing partnerships with educational resource companies, and more.',
                            'link_text': 'Learn about OpenStax',
                            'link_href': 'https://openstax.org/about-us'
                            },
                }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box",
                  "value": [{"heading": "Expert Authors",
                               "text": "Our open source textbooks are written by professional content developers who are experts in their fields."},
                             {"heading": "Standard Scope and Sequence",
                               "text": "All textbooks meet standard scope and sequence requirements, making them seamlessly adaptable into existing courses.."},
                             {"heading": "Peer Reviewed",
                               "text": "OpenStax textbooks undergo a rigorous peer review process. You can view the list of contributors when you click on each book."},
                           ]
                }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."
        )
        homepage.add_child(instance=subjects_page)
        revision = subjects_page.save_revision()
        revision.publish()
        subjects_page.save()

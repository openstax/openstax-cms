import json
from django.core.management.base import BaseCommand
from pages.models import HomePage, Impact

class Command(BaseCommand):
    help = "create initial impact page after a deployment"

    def handle(self, *args, **options):
        homepage = HomePage.objects.first() # there's only one home page, so this should be okay
        impact_page = Impact(
            title="Our Impact",
            improving_access=json.dumps([
                {"type": "content",
                  "value": {"heading": "Improving Educational Access and Learning for Everyone",
                            "description": "<p>Based at Rice University, OpenStax is one of the world\u2019s largest nonprofit digital learning platforms and publisher of free, open education resources. Join us and help millions of students experience an affordable, engaging education.</p>",
                            "button_text": "Give today", "button_href": "https://openstax.org/give"}}
            ]),
            reach=json.dumps([
                {"type": "content",
                  "value": {"heading": "Our Reach",
                            "description": "<p><b>COVID-19 Impact:</b> Demand for OpenStax more than doubled in the pandemic, so our team rapidly increased learning resources to support instructors and their students with virtual learning. Please make a gift to help us continue to meet this urgent need.</p>",
                            "cards": [{"description": "$1.2 billion saved in education costs since 2012",
                                       "link_text": "Read more", "link_href": "https://openstax.org"},
                                      {"description": "4 million students from 120 countries use OpenStax",
                                       "link_text": "See the map", "link_href": "https://openstax.org"
                                       },
                                      {"description": "60 percent of higher education institutions in US use OpenStax",
                                       "link_text": "",  "link_href": ""
                                       },
                                      {"description": "4 thousand+ K-12 schools use OpenStax",
                                       "link_text": "", "link_href": ""}]
                            },
                }
            ]),
            quote=json.dumps([
                {"type": "content",
                  "value": {"quote": "<p>Amidst COVID-19, educational problems are complex and in constant flux, making it critical that we support students in their learning. OpenStax is expanding its library to new subject areas, deepening student engagement with our digital learning tools, and advancing the frontiers of learning science to help make education engaging and personal. It is through this personalization that we believe we can bring greater equity and quality to education for students worldwide.</p><p></p><p><b>\u2013 Dr. Richard Baraniuk,</b></p><p>Founder of OpenStax, Victor E. Cameron Professor of Electrical and Computer Engineering at Rice University, and Fellow of the American Academy of Arts and Sciences</p>"},
                }
            ]),
            making_a_difference=json.dumps([
                {"type": "content", "value": {"heading": "Making a Difference",
                                               "description": "<p>Learn more from those who have been directly impacted by OpenStax.</p>",
                                               }}
            ]),
            disruption=json.dumps([
                {"type": "content", "value": {"heading": "Positive Disruption",
                                               "description": "The price of textbooks is declining due to open education\u2019s disruption of the college textbook market, removing financial barriers to advanced education, and reducing student debt. According to an economist, \u201cThe \u2018textbook bubble\u2019 is finally starting to deflate, due to the creative destruction and competition from free/low-cost textbooks from groups like OpenStax\u201d (Mark Perry, AEI, 2019).",
                                               "graph": {
                                                   "top_caption": "Consumer Price Index Educational Books and Supplies, January 1967 to September 2017",
                                                   "bottom_caption": "<p>https://www.aei.org/publication/wednesday-afternoon-links-30/</p><p>Published by Mark Perry on October 25, 2017, AEI.org</p>",
                                                }},
                }
            ]),
            supporter_community=json.dumps([
                {"type": "content", "value": {"heading": "Our Supporter Community",
                                               "quote": "<p>OpenStax continues to expand to new subject areas, grade levels, and languages to reach more students. Yet, OpenStax is more than free textbooks. With a team of researchers, educators, and learning engineers at Rice University, OpenStax is creating research-based learning tools to help teachers and learners better personalize the education experience. OpenStax needs your partnership to continue its impact.</p><p></p><p>\u2013 <b>Ann Doerr</b>, OpenStax Advisor</p>",
                                               "link_text": "View our supporters", "link_href": "https://openstax.org"},
                }
            ]),
            giving=json.dumps([
                {"type": "content", "value": {"heading": "Students need your help today.",
                                               "description": "Together, we can increase educational equity and quality for millions of students worldwide.",
                                               "link_text": "Give today", "link_href": "https://openstax.org/give",
                                               "nonprofit_statement": "As a part of Rice University, a 501(c)(3) nonprofit, gifts to OpenStax are tax deductible to the fullest extent allowed by law. Our tax ID number is 74-1109620. Read our latest Annual Report",
                                               "annual_report_link_text": "Read our latest Annual Report", "annual_report_link_href": "https://openstax.org/"},
                }
            ])
        )

        homepage.add_child(instance=impact_page)
        revision = impact_page.save_revision()
        revision.publish()
        impact_page.save()

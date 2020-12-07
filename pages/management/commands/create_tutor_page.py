import json
from django.core.management.base import BaseCommand
from pages.models import HomePage, TutorMarketing

class Command(BaseCommand):
    help = "create initial tutor marketing page after a deployment"

    def handle(self, *args, **options):
        homepage = HomePage.objects.first() # there's only one home page, so this should be okay
        tutor_page = TutorMarketing(
            title="Tutor Marketing",
            header="Courseware for online, in-person, and hybrid classrooms.",
            description="Next semester, support long-term learning and reading comprehension with OpenStax Tutor. Our research-based tool gives students the easy-to-use online courseware they need to stay engaged while reading and doing homework assignments. And you get insight into how your students are learning and where they need extra support.",
            header_cta_button_text="Schedule a demo",
            header_cta_button_link="https://openstax.org",
            quote="I don’t know how or where you found this program, but it is by far the best study and learning tool I have ever used. The Pearson MyLab and the Matlab tools are nowhere near as user-friendly, and the ease of access the tutor offers is incredibly helpful for me (I’m not the most technologically capable on a good day). The in-reading questions help tremendously in remembering information and locking-in what I am currently reading. — <b>Person Name</b>, Title, Organization",
            features_header="How OpenStax Tutor works",
            features_cards=json.dumps([
                {"type": "cards", "value": {"title": "Title lorem ipsum", "description": "<p>We break textbook readings into easy to digest segments with videos, simulations, and conceptual questions.</p>"}},
                {"type": "cards", "value": {"title": "Title lorem ipsum", "description": "<p>Spaced practice, personalized questions, and other features help students learn more efficiently and effectively.</p>"}},
                {"type": "cards", "value": {"title": "Title lorem ipsum", "description": "<p>You can build homework assignments with questions from the book, additional assessments, and personalized questions.</p>"}},
            ]),
            available_books_header="Available Books",
            cost_header="Here’s how our pricing works",
            cost_description="We keep our costs low and provide OpenStax Tutor for $10, allowing us to support the tool and make research-backed improvements. We also have free options for Institutional Partner schools and high schools – find your options below.",
            cost_cards=json.dumps([
                {"type": "cards", "value": {"title": "Colleges and universities", "description": "<p>All courses are <b>$10 per student, per semester</b>. This allows us to support the tool and make research-backed improvements.</p>"}},
                {"type": "cards", "value": {"title": "AP US History", "description": "<p>Our AP U.S. History course is <b>FREE</b> for everyone!</p>"}},
            ]),
            cost_institution_message="Institutions can also buy OpenStax Tutor for their students directly from OpenStax. <a href=''>Contact us</a> to get started.",
            feedback_heading="What others are saying",
            feedback_quote="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla eleifend fermentum magna fermentum varius. In quis augue dui. Praesent congue dignissim scelerisque.",
            feedback_name="Person Name",
            feedback_occupation="Occupation",
            feedback_organization="Organization",
            webinars_header="Get more info from our webinars",
            faq_header="Frequently asked questions",
            demo_cta_text="Schedule a Demo",
            demo_cta_link="https://openstax.org",
            tutor_login_link="https://tutor.openstax.org"
        )

        homepage.add_child(instance=tutor_page)
        revision = tutor_page.save_revision()
        revision.publish()
        tutor_page.save()

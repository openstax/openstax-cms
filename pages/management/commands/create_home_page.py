import json
from django.core.management.base import BaseCommand
from pages.models import HomePage

class Command(BaseCommand):
    help="Populate home page after a deployment"

    def handle(self, *args, **options):
        homepage = HomePage.objects.first()

        homepage.banner_headline="Free and flexible textbooks and resources."
        homepage.banner_description="<b>Create a free account</b> for full access to our free textbooks and resources."
        homepage.banner_get_started_text="Get started now"
        homepage.banner_get_started_link="https://accounts.openstax.org/accounts/i/login/?r=https://openstax.org/"
        homepage.banner_login_text="Login"
        homepage.banner_login_link="https://accounts.openstax.org/accounts/i/login/?r=https://openstax.org/"
        homepage.banner_logged_in_text="Explore Now"
        homepage.banner_logged_in_link="https://openstax.org/subjects"
        homepage.features_headline="More than just books."
        homepage.features_tab1_heading="For Instructors"
        homepage.features_tab2_heading="For Students"
        homepage.features_tab1_features=json.dumps(
            [{"type": "feature_text", "value": "LMS Integration"},
             {"type": "feature_text", "value": "Test banks"},
             {"type": "feature_text", "value": "Answer guides"},
             {"type": "feature_text", "value": "Powerpoint slides"}]
        )
        homepage.features_tab1_explore_text="Explore now"
        homepage.features_tab1_explore_url="https://openstax.org/subjects"
        homepage.features_tab1_explore_logged_in_text="Explore Now"
        homepage.features_tab1_explore_logged_in_url="https://openstax.org/subjects"
        homepage.features_tab2_features = json.dumps(
            [{"type": "feature_text", "value": "Highlighting"},
             {"type": "feature_text", "value": "Note-taking"},
             {"type": "feature_text", "value": "Multiple different book formats"},
             {"type": "feature_text", "value": "Low cost or free"}]
        )
        homepage.features_tab2_explore_text="Explore Now"
        homepage.features_tab2_explore_url="https://openstax.org/subjects"
        homepage.quotes_headline="Improving education for students and instructors."
        homepage.quotes=json.dumps(
            [{"type": "quote",
              "value": [{
                         "testimonial": 'I was assigned the OpenStax Psychology textbook in my first psychology course. <b>I thought it was great that the book was free online.</b> I thought it was even better that I could get the physical book, brand new for $30 because that"s how I learn best. <b>I feel like the book helped my instructor bring in more real world, relatable examples because it was so current.</b>',
                         "author": "Christine Mompoint, student at Houston Community College"
                        },
                        {
                         "testimonial": "OpenStax has changed the way I teach this subject and the way my students navigate the learning process.",
                         "author": "Instructor at Midlands College"
                        }]

              }
            ])
        homepage.tutor_description="OpenStax Tutor, our courseware platform, costs only $10 per student, and enables better learning for your students and easy course creation for you. With digital reading, personalized homework, a library of thousands of assessments, and LMS integration, OpenStax Tutorworks well for online, hybrid, and in-person courses."
        homepage.tutor_button_text="About Openstax Tutor"
        homepage.tutor_button_link="https://openstax.org/openstax-tutor"
        homepage.tutor_demo_text="Schedule a demo"
        homepage.tutor_demo_link="https://calendly.com/creighton-2"
        homepage.whats_openstax_headline="What’s OpenStax"
        homepage.whats_openstax_description="OpenStax is part of Rice University, which is a 501(c)(3) nonprofit charitable corporation. Our mission is to improve educational access and learning for everyone. We do this by publishing openly licensed books, developing and improving research-based courseware, establishing partnerships with educational resource companies, and more."
        homepage.whats_openstax_donate_text="We couldn’t do what we do without the help of our generous supporters."
        homepage.whats_openstax_give_text="Give today"
        homepage.whats_openstax_give_link="https://openstax.org/give"
        homepage.whats_openstax_learn_more_text="Learn more about OpenStax"
        homepage.whats_openstax_learn_more_link="https://openstax.org/about"

        homepage.save()
        revision = homepage.save_revision()
        revision.publish()

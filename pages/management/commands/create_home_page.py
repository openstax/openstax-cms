import json
from django.core.management.base import BaseCommand
from pages.models import HomePage

class Command(BaseCommand):
    help="create initial home page after a deployment"

    def handle(self, *args, **options):
        home_page = HomePage(
            banner_headline='Free and flexible textbooks and resources.',
            banner_description='<b>Create a free account</b> for full access to our free textbooks and resources.',
            banner_get_started_text='Get started now',
            banner_get_started_link='https://accounts.openstax.org/accounts/i/login/?r=https%3A%2F%2Fopenstax.org%2Ferror%2F404%3Fpath%3D%2Flogin',
            banner_login_text='Login',
            banner_login_link='https://accounts.openstax.org/accounts/i/login/?r=https%3A%2F%2Fopenstax.org%2Ferror%2F404%3Fpath%3D%2Flogin',
            banner_logged_in_text='??',
            banner_logged_in_link='??',
            features_headline='More than just books.',
            features_tab1_heading='For Instructors',
            features_tab2_heading='For Students',
            features_tab1_explore_text='Explore now',
            features_tab1_explore_url='??',
            features_tab1_explore_logged_in_text='??',
            features_tab1_explore_logged_in_url='??',
            features_tab2_explore_text='Explore Now',
            features_tab2_explore_url='??',
            quotes_headline='Improving education for students and instructors.',
            quotes=json.dumps([
                {"type": "content", "value": {"testimonial": "I was assigned the OpenStax Psychology textbook in my first psychology course. <b>I thought it was great that the book was free online.</b> I thought it was even better that I could get the physical book, brand new for $30 because that's how I learn best. <b>I feel like the book helped my instructor bring in more real world, relatable examples because it was so current.</b>",
                                              "author": "Christine Mompoint, student at Houston Community College",
                                              }
                 },
                {"type": "content", "value": {
                    "testimonial": "OpenStax has changed the way I teach this subject and the way my students navigate the learning process.",
                    "author": "Instructor at Midlands College",
                    },
                 }
            ]),
            tutor_description='OpenStax Tutor, our courseware platform, costs only $10 per student, and enables better learning for your students and easy course creation for you. With digital reading, personalized homework, a library of thousands of assessments, and LMS integration, OpenStax Tutorworks well for online, hybrid, and in-person courses.',
            tutor_button_text='About Openstax Tutor',
            tutor_button_link='https://openstax.org/openstax-tutor',
            tutor_demo_text='Schedule a demo',
            tutor_demo_link='??',
            tutor_features_cards=json.dumps([
                {"type": "cards", "value": {"title": "Title lorem ipsum", "description": "<p>We break textbook readings into easy to digest segments with videos, simulations, and conceptual questions.</p>"}},
                {"type": "cards", "value": {"title": "Title lorem ipsum", "description": "<p>Spaced practice, personalized questions, and other features help students learn more efficiently and effectively.</p>"}},
                {"type": "cards", "value": {"title": "Title lorem ipsum", "description": "<p>You can build homework assignments with questions from the book, additional assessments, and personalized questions.</p>"}},
            ]),
            whats_openstax_headline='What’s OpenStax',
            whats_openstax_description='OpenStax is part of Rice University, which is a 501(c)(3) nonprofit charitable corporation. Our mission is to improve educational access and learning for everyone. We do this by publishing openly licensed books, developing and improving research-based courseware, establishing partnerships with educational resource companies, and more.',
            whats_openstax_donate_text='We couldn’t do what we do without the help of our generous supporters.',
            whats_openstax_give_text='Give today',
            whats_openstax_give_link='https://openstax.org/give',
            whats_openstax_learn_more_text='Learn more about OpenStax',
            whats_openstax_learn_more_link='https://openstax.org/about'
        )

        revision = home_page.save_revision()
        revision.publish()
        home_page.save()

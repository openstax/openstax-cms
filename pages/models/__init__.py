"""Public API of the pages app's models.

The page models are split across themed submodules; everything is re-exported
here so ``from pages.models import X`` keeps working for code, migrations, and
``patch('pages.models.X...')`` targets. Django identifies models by app label
and class name, so the module split produces no migrations.
"""
# Historic migrations and external tests reference these via pages.models.
from wagtail.models import Page
from pages.custom_blocks import APIImageChooserBlock

from .constants import (
    HERO_IMAGE_ALIGNMENT_CHOICES,
    BASE_CONTENT_BLOCKS,
    SECTION_CONTENT_BLOCKS,
    BODY_BLOCKS,
)
from .bases import Quote, Institutions, Group
from .core import RootPage, FlexPageRelatedPage, FlexPage, HomePage, GeneralPage
from .about import AboutUsPage, OpenStaxPeople, TeamPage, LearningResearchPage, Careers
from .giving import Supporters, MapPage, Give, GiveForm, ImpactStory, Impact
from .legal import TermsOfService, Accessibility, Licensing, PrivacyPolicy
from .support import ContactUs, FAQ, ErrataList, PrintOrder, FormHeadings
from .partners import (
    Technology,
    InstitutionalPartnership,
    InstitutionalPartnerProgramPage,
    PartnersPage,
)
from .marketing import (
    CreatorFestPage,
    WebinarPage,
    PartnerChooserBlock,
    MathQuizPage,
    LLPHPage,
    TutorMarketing,
    AllyLogos,
    Assignable,
)
from .subjects import Subjects, SubjectOrderable, Subject
from .k12 import K12MainPage, K12Subject

from .models import (HomePage,
                     HigherEducation,
                     GeneralPage,
                     ContactUs,
                     AboutUs,
                     EcosystemAllies,
                     FoundationSupport,
                     OurImpact,
                     Give,
                     TermsOfService,
                     AP,
                     FAQ,
                     Support)
from wagtail.contrib.wagtailapi.serializers import PageSerializer


class HomePageSerializer(PageSerializer):
    class Meta:
        model = HomePage
        fields = HomePage.api_fields


class HigherEducationSerializer(PageSerializer):
    class Meta:
        model = HigherEducation
        fields = HigherEducation.api_fields


class GeneralPageSerializer(PageSerializer):
    class Meta:
        model = GeneralPage
        fields = GeneralPage.api_fields


class ContactUsSerializer(PageSerializer):
    class Meta:
        model = ContactUs
        fields = ContactUs.api_fields


class AboutUsSerializer(PageSerializer):
    class Meta:
        model = AboutUs
        fields = AboutUs.api_fields


class EcosystemAlliesSerializer(PageSerializer):
    class Meta:
        model = EcosystemAllies
        fields = EcosystemAllies.api_fields


class FoundationSupportSerializer(PageSerializer):
    class Meta:
        model = FoundationSupport
        fields = FoundationSupport.api_fields


class OurImpactSerializer(PageSerializer):
    class Meta:
        model = OurImpact
        fields = OurImpact.api_fields


class GiveSerializer(PageSerializer):
    class Meta:
        model = Give
        fields = Give.api_fields


class TermsOfServiceSerializer(PageSerializer):
    class Meta:
        model = TermsOfService
        fields = TermsOfService.api_fields


class APSerializer(PageSerializer):
    class Meta:
        model = AP
        fields = AP.api_fields


class FAQSerializer(PageSerializer):
    class Meta:
        model = FAQ
        fields = FAQ.api_fields


class SupportSerializer(PageSerializer):
    class Meta:
        model = Support
        fields = Support.api_fields

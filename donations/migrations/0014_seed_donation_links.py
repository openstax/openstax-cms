from django.db import migrations

PUBLIC_GOOD_SUBTITLE = (
    "Join us in sustaining OpenStax as a public good for years to come by giving today."
)

# Mirrors the hardcoded pairs in os-webview's use-give-links.ts so behavior is
# unchanged on deploy; from here on, marketing edits these in the CMS instead.
DONATION_LINKS = (
    ('pdf', 'control', 'https://riceconnect.rice.edu/donation/support-openstax-subject', ''),
    ('pdf', 'public good', 'https://riceconnect.rice.edu/donation/support-openstax-subject-b', PUBLIC_GOOD_SUBTITLE),
    ('instructor_resources', 'control',
     'https://riceconnect.rice.edu/donation/support-openstax-instructor-resources', ''),
    ('instructor_resources', 'public good',
     'https://riceconnect.rice.edu/donation/support-openstax-instructor-resources-b', PUBLIC_GOOD_SUBTITLE),
    ('student_resources', 'control',
     'https://riceconnect.rice.edu/donation/support-openstax-student-resources', ''),
    ('student_resources', 'public good',
     'https://riceconnect.rice.edu/donation/support-openstax-student-resources-b', PUBLIC_GOOD_SUBTITLE),
    ('other', 'control', 'https://riceconnect.rice.edu/donation/support-openstax-subject', ''),
    ('other', 'public good', 'https://riceconnect.rice.edu/donation/support-openstax-subject-b',
     PUBLIC_GOOD_SUBTITLE),
)


def seed_donation_links(apps, schema_editor):
    DonationLink = apps.get_model('donations', 'DonationLink')
    for placement, variant, url, header_subtitle in DONATION_LINKS:
        DonationLink.objects.update_or_create(
            placement=placement,
            variant=variant,
            defaults={'url': url, 'header_subtitle': header_subtitle, 'is_active': True},
        )


def remove_seeded_donation_links(apps, schema_editor):
    DonationLink = apps.get_model('donations', 'DonationLink')
    for placement, variant, _url, _header_subtitle in DONATION_LINKS:
        DonationLink.objects.filter(placement=placement, variant=variant).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("donations", "0013_donationlink"),
    ]

    operations = [
        migrations.RunPython(seed_donation_links, remove_seeded_donation_links),
    ]

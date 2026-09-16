from django.db import migrations

DEFAULT_GIVE_LINK = 'https://riceconnect.rice.edu/donation/support-openstax-header'


def seed_default_give_link(apps, schema_editor):
    GiveToday = apps.get_model('global_settings', 'GiveToday')
    GiveToday.objects.update(default_give_link=DEFAULT_GIVE_LINK)


def clear_default_give_link(apps, schema_editor):
    GiveToday = apps.get_model('global_settings', 'GiveToday')
    GiveToday.objects.filter(default_give_link=DEFAULT_GIVE_LINK).update(default_give_link='')


class Migration(migrations.Migration):

    dependencies = [
        ("global_settings", "0024_givetoday_default_give_link"),
    ]

    operations = [
        migrations.RunPython(seed_default_give_link, clear_default_give_link),
    ]

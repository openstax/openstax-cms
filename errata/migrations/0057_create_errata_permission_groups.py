from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

DEFAULT_ERRATA_PERMISSION_CODENAMES = ['add_errata', 'change_errata', 'view_errata']
ERRATA_GROUP_NAMES = ('Content Managers', 'Editorial Vendor')


def create_errata_permission_groups(apps, schema_editor):
    # Permissions are normally created by Django's post_migrate signal, which
    # only fires after every app's migrations finish in this run - too late
    # for a data migration that needs to query Permission rows for this app
    # on a from-scratch database (fresh dev DB, CI). Force creation now.
    create_permissions(global_apps.get_app_config('errata'), apps=apps, verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    default_permissions = Permission.objects.filter(
        content_type__app_label='errata',
        content_type__model='errata',
        codename__in=DEFAULT_ERRATA_PERMISSION_CODENAMES,
    )

    for group_name in ERRATA_GROUP_NAMES:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            group.permissions.set(default_permissions)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('errata', '0056_alter_errata_options'),
        ('auth', '__first__'),
    ]

    operations = [
        migrations.RunPython(create_errata_permission_groups, noop),
    ]

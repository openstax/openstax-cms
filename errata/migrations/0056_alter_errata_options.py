# Generated by Django 4.1.7 on 2023-11-17 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('errata', '0055_remove_errata_accounts_user_email_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='errata',
            options={'verbose_name': 'erratum list', 'verbose_name_plural': 'errata list'},
        ),
    ]
# Generated by Django 2.2.8 on 2020-02-19 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0225_webinarpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerspage',
            name='partner_landing_page_link',
            field=models.CharField(blank=True, help_text='Link text to partner landing page.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='partnerspage',
            name='partner_request_info_link',
            field=models.CharField(blank=True, help_text='Forstack form link text', max_length=255, null=True),
        ),
    ]
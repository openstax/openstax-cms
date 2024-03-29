# Generated by Django 4.0.8 on 2023-06-13 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0049_pressindex_about_alter_pressindex_mentions'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsindex',
            name='display_footer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='newsindex',
            name='footer_button_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='newsindex',
            name='footer_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='newsindex',
            name='footer_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

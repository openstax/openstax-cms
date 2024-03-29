# Generated by Django 3.2.9 on 2022-03-28 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0096_salesforceforms_debug_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partner',
            name='formstack_url',
        ),
        migrations.AddField(
            model_name='partner',
            name='autonomy_summative_assessments',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='customization_content_repository',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='feedback_individual_and_groups',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='instructional_level_higher_ed',
            field=models.BooleanField(default=False),
        ),
    ]

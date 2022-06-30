# Generated by Django 3.2.5 on 2022-06-14 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailforms', '0004_add_verbose_name_plural'),
        ('wagtailredirects', '0007_add_autocreate_fields'),
        ('wagtailcore', '0066_collection_management_permissions'),
        ('pages', '0062_alter_impactstory_body'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ap',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='ap',
            name='promote_image',
        ),
        migrations.RemoveField(
            model_name='compcopy',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='compcopy',
            name='promote_image',
        ),
        migrations.RemoveField(
            model_name='herojourneypage',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='highereducation',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='highereducation',
            name='promote_image',
        ),
        migrations.RemoveField(
            model_name='interestform',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='interestform',
            name='promote_image',
        ),
        migrations.RemoveField(
            model_name='support',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='support',
            name='promote_image',
        ),
        migrations.RemoveField(
            model_name='tutorlanding',
            name='case_study_file',
        ),
        migrations.RemoveField(
            model_name='tutorlanding',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='tutorlanding',
            name='promote_image',
        ),
        migrations.DeleteModel(
            name='AdoptForm',
        ),
        migrations.DeleteModel(
            name='AP',
        ),
        migrations.DeleteModel(
            name='CompCopy',
        ),
        migrations.DeleteModel(
            name='HeroJourneyPage',
        ),
        migrations.DeleteModel(
            name='HigherEducation',
        ),
        migrations.DeleteModel(
            name='InterestForm',
        ),
        migrations.DeleteModel(
            name='Support',
        ),
        migrations.DeleteModel(
            name='TutorLanding',
        ),
    ]
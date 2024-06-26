# Generated by Django 4.0.8 on 2023-06-01 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0145_remove_book_assignable_book_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facultyresources',
            name='link_external',
            field=models.URLField(blank=True, help_text='Provide an external URL starting with https:// (or fill out either one of the following two).', null=True, verbose_name='External link'),
        ),
        migrations.AlterField(
            model_name='facultyresources',
            name='link_text',
            field=models.CharField(blank=True, help_text='Call to Action Text', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='studentresources',
            name='link_external',
            field=models.URLField(blank=True, help_text='Provide an external URL starting with http:// (or fill out either one of the following two).', null=True, verbose_name='External link'),
        ),
        migrations.AlterField(
            model_name='studentresources',
            name='link_text',
            field=models.CharField(blank=True, help_text='Call to Action Text', max_length=255, null=True),
        ),
    ]

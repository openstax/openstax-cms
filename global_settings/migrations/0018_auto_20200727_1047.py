# Generated by Django 3.0.4 on 2020-07-27 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0017_auto_20200325_1058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stickynote',
            old_name='content',
            new_name='body',
        ),
        migrations.RemoveField(
            model_name='stickynote',
            name='show',
        ),
        migrations.AddField(
            model_name='stickynote',
            name='header',
            field=models.TextField(default=' ', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stickynote',
            name='link',
            field=models.URLField(default=' '),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stickynote',
            name='link_text',
            field=models.CharField(default=' ', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stickynote',
            name='start',
            field=models.DateTimeField(help_text='Set the start date to override the content of the Give Sticky. Set the header and body below to change.', null=True),
        ),
        migrations.AlterField(
            model_name='stickynote',
            name='emergency_expires',
            field=models.DateTimeField(blank=True, help_text='When active, the Sticky Note will not be displayed until the emergency expires.', null=True),
        ),
        migrations.AlterField(
            model_name='stickynote',
            name='expires',
            field=models.DateTimeField(help_text='Set the date to expire overriding the content of the Give Sticky.', null=True),
        ),
    ]

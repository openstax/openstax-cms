# Generated by Django 4.0.8 on 2023-02-03 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0024_index_image_file_hash'),
        ('snippets', '0024_k12subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='facultyresource',
            name='icon',
            field=models.ForeignKey(blank=True, help_text='icon used on K12 Subject pages', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
        migrations.AddField(
            model_name='studentresource',
            name='icon',
            field=models.ForeignKey(blank=True, help_text='icon used on K12 Subject pages', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
        migrations.AlterField(
            model_name='k12subject',
            name='subject_category',
            field=models.CharField(choices=[('Math', 'Math'), ('Social Studies', 'Social Studies'), ('Science', 'Science'), ('English Language Areas & Reading', 'English Language Areas & Reading'), ('Career and Technical Education', 'Career and Technical Education'), ('College Readiness', 'College Readiness'), ('Fine Arts', 'Fine Arts'), ('Health Education', 'Health Education'), ('Languages other than English', 'Languages other than English'), ('Physical Education', 'Physical Education'), ('Technology Applications', 'Technology Applications'), ('Other', 'Other'), ('None', 'None')], default='None', help_text='The category used in the K12 subjects listings', max_length=255),
        ),
    ]

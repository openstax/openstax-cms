# Generated by Django 3.0.4 on 2020-10-12 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0057_partner_instructional_level_k12'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='international',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='online_teaching_academic_integrity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='online_teaching_asynchronous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='online_teaching_audio_video',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='online_teaching_in_lecture',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='online_teaching_lecture_streaming',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='online_teaching_peer_discussion',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partner',
            name='online_teaching_teaching_labs',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 3.0.4 on 2021-05-25 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ThankYouNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thank_you_note', models.TextField(blank=True, null=True)),
                ('user_info', models.TextField(blank=True, null=True)),
                ('created', models.DateField(auto_now_add=True)),
            ],
        ),
    ]

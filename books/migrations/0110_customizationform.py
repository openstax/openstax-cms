# Generated by Django 3.0.4 on 2020-09-22 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0109_customizationrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomizationForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_header', models.CharField(max_length=255)),
                ('form_subheader', models.CharField(max_length=255)),
                ('disclaimer', models.TextField()),
            ],
        ),
    ]

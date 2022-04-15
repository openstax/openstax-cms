# Generated by Django 3.2.5 on 2022-03-28 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_featureflag_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebviewSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
    ]
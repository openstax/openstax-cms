# Generated by Django 3.2.5 on 2022-05-09 15:39

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('snippets', '0019_givebanner'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentLicense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('license_code', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=255, null=True)),
                ('license_name', models.CharField(blank=True, max_length=255, null=True)),
                ('license_url', models.URLField(blank=True, null=True)),
                ('locale', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale')),
            ],
            options={
                'abstract': False,
                'unique_together': {('translation_key', 'locale')},
            },
        ),
    ]
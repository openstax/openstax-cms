# Generated by Django 3.2.9 on 2022-01-27 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('snippets', '0015_rename_subjectcategories_subjectcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
    ]
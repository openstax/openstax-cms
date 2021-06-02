# Generated by Django 3.0.4 on 2021-05-06 18:47

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0041_auto_20210506_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='features_tab1_features',
            field=wagtail.core.fields.StreamField([('feature_text', wagtail.core.blocks.CharBlock())]),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='features_tab2_features',
            field=wagtail.core.fields.StreamField([('feature_text', wagtail.core.blocks.CharBlock())]),
        ),
    ]
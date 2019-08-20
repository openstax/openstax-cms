# Generated by Django 2.0.13 on 2019-08-05 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0074_merge_20190805_1353'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='study_edge_link',
            field=models.URLField(blank=True, help_text='Link to Study Edge app. This will cause the link to appear on the book details page.'),
        ),
    ]
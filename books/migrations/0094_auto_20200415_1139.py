# Generated by Django 3.0.4 on 2020-04-15 16:39

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0010_document_file_hash'),
        ('books', '0093_merge_20200403_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=wagtail.core.fields.StreamField([('author', wagtail.core.blocks.StructBlock([('name', wagtail.core.blocks.CharBlock(help_text='Full name of the author.', required=True)), ('university', wagtail.core.blocks.CharBlock(help_text='Name of the university/institution the author is associated with.', required=False)), ('country', wagtail.core.blocks.CharBlock(help_text='Country of the university/institution.', required=False)), ('senior_author', wagtail.core.blocks.BooleanBlock(help_text='Whether the author is a senior author. (Senior authors are shown before non-senior authors.)', required=False)), ('display_at_top', wagtail.core.blocks.BooleanBlock(help_text='Whether display the author on top.', required=False))]))], null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='book_state',
            field=models.CharField(choices=[('live', 'Live'), ('coming_soon', 'Coming Soon'), ('deprecated', 'Deprecated (Disallow errata submissions)'), ('retired', 'Retired (Remove from website)')], default='live', help_text='The state of the book.', max_length=255),
        ),
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ForeignKey(help_text='The book cover to be shown on the website.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document'),
        ),
        migrations.AlterField(
            model_name='book',
            name='publish_date',
            field=models.DateField(help_text='Date the book is published on.', null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='title_image',
            field=models.ForeignKey(help_text='The svg for title image to be shown on the website.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document'),
        ),
    ]
# Generated by Django 2.2.8 on 2020-02-13 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('errata', '0038_auto_20200127_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtext',
            name='email_case',
            field=models.CharField(blank=True, choices=[('Created in fall', 'Created in fall'), ('Created in spring', 'Created in spring'), ('Reviewed and (will not fix, or duplicate, or not an error, or major book revision)', 'Reviewed and (will not fix, or duplicate, or not an error, or major book revision)'), ('Reviewed and Approved', 'Reviewed and Approved'), ('Completed and Sent to Customer Support', 'Completed and Sent to Customer Support'), ('More Information Requested', 'More Information Requested'), ('Getting new edition', 'Getting new edition')], max_length=100, null=True),
        ),
    ]
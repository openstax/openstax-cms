# Generated by Django 3.0.4 on 2020-10-05 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0059_auto_20201005_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerreview',
            name='partner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='salesforce.Partner'),
        ),
    ]
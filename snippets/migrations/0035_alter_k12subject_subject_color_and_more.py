# Generated by Django 5.0.2 on 2024-04-01 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snippets", "0034_delete_assignableavailable"),
    ]

    operations = [
        migrations.AlterField(
            model_name="k12subject",
            name="subject_color",
            field=models.CharField(
                choices=[
                    ("blue", "Blue"),
                    ("midnight", "Midnight"),
                    ("deep-green", "Deep Green"),
                    ("gold", "Gold"),
                    ("gray", "Gray"),
                    ("green", "Green"),
                    ("light-blue", "Light Blue"),
                    ("light-gray", "Light Gray"),
                    ("medium-blue", "Medium Blue"),
                    ("orange", "Orange"),
                    ("red", "Red"),
                    ("yellow", "Yellow"),
                ],
                default="blue",
                help_text="The color of the vertical stripe on Subject page.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="subject",
            name="subject_color",
            field=models.CharField(
                choices=[
                    ("blue", "Blue"),
                    ("midnight", "Midnight"),
                    ("deep-green", "Deep Green"),
                    ("gold", "Gold"),
                    ("gray", "Gray"),
                    ("green", "Green"),
                    ("light-blue", "Light Blue"),
                    ("light-gray", "Light Gray"),
                    ("medium-blue", "Medium Blue"),
                    ("orange", "Orange"),
                    ("red", "Red"),
                    ("yellow", "Yellow"),
                ],
                default="blue",
                help_text="The color of the vertical stripe on Subject page.",
                max_length=255,
            ),
        ),
    ]
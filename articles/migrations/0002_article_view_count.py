# Generated by Django 4.2.8 on 2024-12-26 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="view_count",
            field=models.PositiveIntegerField(default=0, verbose_name="조회수"),
        ),
    ]
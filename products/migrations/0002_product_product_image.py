# Generated by Django 4.2.8 on 2024-12-29 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="product_image",
            field=models.ImageField(null=True, upload_to="products/"),
        ),
    ]

# Generated by Django 5.0.1 on 2024-06-02 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_management', '0002_remove_staff_subscription_expiry_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='subscription_status',
            field=models.BooleanField(default=False),
        ),
    ]

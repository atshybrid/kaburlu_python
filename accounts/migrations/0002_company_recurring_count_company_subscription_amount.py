# Generated by Django 5.0.1 on 2024-06-10 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='recurring_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='subscription_amount',
            field=models.IntegerField(default=200000),
        ),
    ]

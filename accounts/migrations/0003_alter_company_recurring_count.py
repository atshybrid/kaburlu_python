# Generated by Django 5.0.1 on 2024-06-10 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_company_recurring_count_company_subscription_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='recurring_count',
            field=models.IntegerField(default=12),
        ),
    ]
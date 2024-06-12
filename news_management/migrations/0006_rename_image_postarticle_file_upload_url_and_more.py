# Generated by Django 5.0.1 on 2024-06-04 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_management', '0005_alter_staff_subscription_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='postarticle',
            old_name='image',
            new_name='file_upload_url',
        ),
        migrations.RemoveField(
            model_name='postarticle',
            name='video',
        ),
        migrations.AlterField(
            model_name='postarticle',
            name='media_type',
            field=models.CharField(choices=[('image', 'Image'), ('video', 'Video'), ('url', 'url')], max_length=100),
        ),
        migrations.AlterField(
            model_name='postarticle',
            name='news_language',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='postarticle',
            name='short_news',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='postarticle',
            name='title1',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='postarticle',
            name='title2',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='postarticle',
            name='title3',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
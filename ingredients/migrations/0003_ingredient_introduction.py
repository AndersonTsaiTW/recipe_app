# Generated by Django 4.2.19 on 2025-03-04 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_ingredient_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='introduction',
            field=models.TextField(blank=True, null=True),
        ),
    ]

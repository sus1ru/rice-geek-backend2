# Generated by Django 4.1.7 on 2023-02-21 17:06

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20230221_0407'),
    ]

    operations = [
        migrations.AddField(
            model_name='predict',
            name='thumbnail',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to=core.models.get_image_path),
        ),
    ]

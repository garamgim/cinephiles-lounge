# Generated by Django 4.2.8 on 2024-05-19 00:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lounges', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lounge',
            name='admin',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='managing_lounges', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

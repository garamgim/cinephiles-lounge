# Generated by Django 4.2.8 on 2024-05-22 03:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lounges', '0004_loungecomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loungearticle',
            name='lounge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to='lounges.lounge'),
        ),
    ]
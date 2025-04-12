# Generated by Django 5.1.6 on 2025-04-02 20:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0063_notification_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentary',
            name='reply_to',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='social_net.commentary'),
        ),
    ]

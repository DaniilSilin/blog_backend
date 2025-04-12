# Generated by Django 5.1.6 on 2025-04-03 06:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0065_alter_commentary_reply_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='post',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='social_net.post'),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.1.6 on 2025-03-13 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0062_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='text',
            field=models.TextField(default=0, verbose_name='Текст уведомления'),
            preserve_default=False,
        ),
    ]

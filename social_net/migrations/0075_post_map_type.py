# Generated by Django 5.2 on 2025-04-21 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0074_notification_parent_comment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='map_type',
            field=models.CharField(choices=[('interactive', 'Интерактивная'), ('static', 'Статическая'), ('null', 'Не выбрано')], default='null', max_length=50, verbose_name='Тип карты'),
        ),
    ]

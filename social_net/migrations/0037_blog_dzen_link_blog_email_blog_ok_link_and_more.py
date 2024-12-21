# Generated by Django 4.1.5 on 2024-11-30 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0036_alter_commentary_dislikes_alter_commentary_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='dzen_link',
            field=models.CharField(blank=True, max_length=255, verbose_name='Ссылка на Дзен'),
        ),
        migrations.AddField(
            model_name='blog',
            name='email',
            field=models.CharField(blank=True, max_length=255, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='blog',
            name='ok_link',
            field=models.CharField(blank=True, max_length=255, verbose_name='Ссылка на ОК'),
        ),
        migrations.AddField(
            model_name='blog',
            name='phone_number',
            field=models.CharField(blank=True, max_length=255, verbose_name='Номер телефона'),
        ),
        migrations.AddField(
            model_name='blog',
            name='site_link',
            field=models.CharField(blank=True, max_length=255, verbose_name='Cсылка на свой сайт'),
        ),
        migrations.AddField(
            model_name='blog',
            name='telegram_link',
            field=models.CharField(blank=True, max_length=255, verbose_name='Ссылка на Telegram'),
        ),
        migrations.AddField(
            model_name='blog',
            name='vk_link',
            field=models.CharField(blank=True, max_length=255, verbose_name='Ссылка на ВК'),
        ),
        migrations.AddField(
            model_name='blog',
            name='youtube_link',
            field=models.CharField(blank=True, max_length=255, verbose_name='Ссылка на YouTube'),
        ),
    ]

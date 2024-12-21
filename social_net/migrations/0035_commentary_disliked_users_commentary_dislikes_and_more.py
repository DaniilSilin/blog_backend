# Generated by Django 4.1.5 on 2024-11-20 10:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social_net', '0034_alter_commentary_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentary',
            name='disliked_users',
            field=models.ManyToManyField(blank=True, related_name='disliked_commentaries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentary',
            name='dislikes',
            field=models.PositiveIntegerField(null=True, verbose_name='Дизлайки'),
        ),
        migrations.AddField(
            model_name='commentary',
            name='liked_users',
            field=models.ManyToManyField(blank=True, related_name='liked_commentaries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentary',
            name='likes',
            field=models.PositiveIntegerField(null=True, verbose_name='Лайки'),
        ),
    ]

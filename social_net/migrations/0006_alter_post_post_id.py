# Generated by Django 4.1.5 on 2023-09-30 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0005_post_post_id_alter_blog_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_id',
            field=models.PositiveIntegerField(unique=True, verbose_name='ID поста'),
        ),
    ]

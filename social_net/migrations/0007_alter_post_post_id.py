# Generated by Django 4.1.5 on 2023-09-30 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0006_alter_post_post_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_id',
            field=models.PositiveIntegerField(verbose_name='ID поста'),
        ),
    ]

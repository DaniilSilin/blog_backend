# Generated by Django 4.1.5 on 2023-10-01 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_net', '0010_alter_blog_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='slug',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]

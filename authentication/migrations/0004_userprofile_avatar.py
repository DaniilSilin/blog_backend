# Generated by Django 4.1.5 on 2024-11-04 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_alter_userprofile_is_admin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default='icy.png', upload_to='images/'),
        ),
    ]

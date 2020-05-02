# Generated by Django 3.0.5 on 2020-05-02 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='disabled',
        ),
        migrations.RemoveField(
            model_name='user',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='email_verified',
        ),
        migrations.RemoveField(
            model_name='user',
            name='photo_url',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='firebase_uid',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.TextField(),
        ),
    ]

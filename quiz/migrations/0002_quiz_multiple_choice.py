# Generated by Django 3.0.6 on 2020-05-28 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='multiple_choice',
            field=models.BooleanField(blank=True, default=True, help_text='Is this going to be a multiple choice quiz?', verbose_name='Yes'),
        ),
    ]

# Generated by Django 4.2.7 on 2023-12-06 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_phase'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_title',
            field=models.CharField(default='Question title', max_length=140),
        ),
    ]
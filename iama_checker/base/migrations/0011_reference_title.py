# Generated by Django 4.2.7 on 2023-12-21 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='title',
            field=models.CharField(default='Example title', max_length=64),
        ),
    ]
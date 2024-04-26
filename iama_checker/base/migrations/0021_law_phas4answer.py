# Generated by Django 5.0.4 on 2024-04-26 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_question_question_context_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Law',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('CP', 'complete'), ('ICP', 'incomplete'), ('CO', 'cut-off')], default='CO', max_length=4)),
                ('assesment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.assesment')),
            ],
        ),
        migrations.CreateModel(
            name='Phas4Answer',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.answer')),
                ('law', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.law')),
            ],
            bases=('base.answer',),
        ),
    ]
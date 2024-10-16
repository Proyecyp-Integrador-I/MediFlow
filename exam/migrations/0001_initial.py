# Generated by Django 5.1 on 2024-10-16 19:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ophthalmologist', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('exam_date', models.DateField(blank=True, null=True)),
                ('analysis_date', models.DateField(blank=True, null=True)),
                ('file', models.FileField(upload_to='uploads/')),
                ('result_analysis', models.TextField(blank=True)),
                ('is_analyzed', models.BooleanField(default=False)),
                ('apparatus', models.CharField(blank=True, max_length=50, null=True)),
                ('exam_type', models.CharField(blank=True, max_length=50, null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ophthalmologist.patient')),
            ],
        ),
    ]

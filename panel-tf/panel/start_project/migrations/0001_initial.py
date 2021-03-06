# Generated by Django 3.0.6 on 2021-09-12 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('startpage', '0002_auth'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_pattern', models.CharField(max_length=128)),
                ('project_group', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='startpage.ProjectGroup')),
            ],
        ),
    ]

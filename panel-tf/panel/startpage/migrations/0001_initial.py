# Generated by Django 3.0.6 on 2021-09-12 18:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(max_length=20)),
                ('name_ru', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Наименование дня недели',
                'verbose_name_plural': 'Наименования дней недели',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='InputType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Тип поля для ввода',
                'verbose_name_plural': 'Типы поля для ввода',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ProjectGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Наименование')),
                ('bitrix_id', models.CharField(max_length=64, verbose_name='Битрикс')),
                ('moysklad_id', models.CharField(max_length=64, verbose_name='МойСклад')),
            ],
            options={
                'verbose_name': 'Группа проекта',
                'verbose_name_plural': 'Группы проектов',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initials', models.CharField(max_length=5)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='MoyskladUser',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('group_id', models.CharField(max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Идентификатор МС',
                'verbose_name_plural': 'Идентификаторы МС',
            },
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('value', models.TextField()),
                ('type', models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='startpage.InputType')),
            ],
            options={
                'verbose_name': 'Поле для ввода',
                'verbose_name_plural': 'Поля для ввода',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='BitrixUser',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Идентификатор в Битрикс',
                'verbose_name_plural': 'Идентификаторы в Битрикс',
            },
        ),
    ]
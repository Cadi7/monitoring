# Generated by Django 3.1.14 on 2022-12-07 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('url', models.URLField(blank=True)),
                ('browser', models.CharField(choices=[('chrome', 'Chrome'), ('firefox', 'Firefox')], default='chrome', max_length=30)),
                ('scheduling', models.CharField(max_length=254)),
                ('next_schedule', models.DateTimeField(default=None, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FlowInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('browser', models.CharField(choices=[('chrome', 'Chrome'), ('firefox', 'Firefox')], default='chrome', max_length=30)),
                ('started_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('success', 'Success'), ('fail', 'Fail')], default='pending', max_length=20)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoring.flow')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_number', models.IntegerField()),
                ('action', models.CharField(choices=[('click', 'Click'), ('tapping', 'Tapping'), ('submit', 'Submit'), ('clear', 'Clear')], max_length=254)),
                ('selector_xpath', models.CharField(max_length=254)),
                ('content', models.CharField(blank=True, max_length=254)),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='monitoring.flow')),
            ],
        ),
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.URLField()),
                ('status', models.CharField(choices=[('initial', 'Initial'), ('success', 'Success'), ('fail', 'Fail'), ('final', 'Final')], default='initial', max_length=20)),
                ('additional_data', models.JSONField(default=dict)),
                ('flow_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoring.flowinstance')),
                ('step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoring.step')),
            ],
        ),
    ]

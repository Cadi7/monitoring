# Generated by Django 3.1.14 on 2022-12-07 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='step_number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
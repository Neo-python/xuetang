# Generated by Django 2.0.1 on 2018-01-28 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0024_auto_20180127_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='delete_status',
            field=models.BooleanField(default=False, verbose_name='删除状态'),
        ),
        migrations.AddField(
            model_name='topic',
            name='delete_status',
            field=models.BooleanField(default=False, verbose_name='删除状态'),
        ),
    ]

# Generated by Django 2.0.1 on 2018-01-30 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0029_tag_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='description',
            field=models.TextField(default='标签还没有描述...', verbose_name='描述'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='icon',
            field=models.FileField(default='/static/img/tag/default.png', upload_to='status/img/tag/', verbose_name='图标'),
        ),
    ]

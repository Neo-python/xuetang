# Generated by Django 2.0.1 on 2018-01-23 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0022_auto_20180122_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicloc',
            name='status',
            field=models.NullBooleanField(verbose_name='赞或反对'),
        ),
    ]

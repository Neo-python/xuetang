# Generated by Django 2.0.1 on 2018-02-06 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20180206_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='addressee',
        ),
        migrations.RemoveField(
            model_name='message',
            name='sender',
        ),
        migrations.AddField(
            model_name='message',
            name='to_user',
            field=models.ForeignKey(default='neo', on_delete=django.db.models.deletion.CASCADE, related_name='m_to_user', to='user.User', to_field='user', verbose_name='接收人'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='to_user_status',
            field=models.BooleanField(default=False, verbose_name='接收人删除状态'),
        ),
        migrations.AddField(
            model_name='message',
            name='user_status',
            field=models.BooleanField(default=False, verbose_name='发送人删除状态'),
        ),
        migrations.AlterField(
            model_name='message',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='m_user', to='user.User', to_field='user', verbose_name='发送人'),
        ),
    ]

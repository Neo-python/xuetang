# Generated by Django 2.0.1 on 2018-01-12 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='分区名')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('icon_path', models.CharField(max_length=200, verbose_name='图标路径')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=200, verbose_name='评论内容')),
                ('floor', models.IntegerField(verbose_name='评论楼层')),
                ('with_floor', models.IntegerField(verbose_name='指向楼层')),
                ('status', models.BooleanField(default=True, verbose_name='评论状态')),
                ('incognito', models.BooleanField(default=False, verbose_name='匿名')),
                ('comment_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User', to_field='nickname', verbose_name='回复对象')),
            ],
        ),
        migrations.CreateModel(
            name='IncognitoComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=200, verbose_name='评论内容')),
                ('with_floor', models.IntegerField(verbose_name='指向楼层')),
                ('status', models.BooleanField(default=False, verbose_name='评论状态')),
                ('comment_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User', to_field='nickname', verbose_name='回复对象')),
            ],
        ),
        migrations.CreateModel(
            name='LikeOrContra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(verbose_name='赞或反对')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='标签名')),
                ('attention', models.IntegerField(default=0, verbose_name='关注数')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='话题标题')),
                ('content', models.TextField(blank=True, verbose_name='话题内容')),
                ('status', models.BooleanField(default=True, verbose_name='显示状态')),
                ('fold_status', models.BooleanField(default=False, verbose_name='折叠状态')),
                ('solve_status', models.BooleanField(default=False, verbose_name='话题终结状态')),
                ('like', models.IntegerField(default=0, verbose_name='赞同数')),
                ('contra', models.IntegerField(default=0, verbose_name='反对数')),
                ('readings', models.IntegerField(default=1, verbose_name='阅读数')),
                ('incognito', models.BooleanField(default=False, verbose_name='匿名状态')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('modify_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('area_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='topic.Area', verbose_name='话题分区')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User', to_field='user', verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='TopicAndTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='topic.Tag', verbose_name='标签')),
                ('topic_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='topic.Topic', verbose_name='话题')),
            ],
        ),
        migrations.AddField(
            model_name='likeorcontra',
            name='topic_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_or_contra', to='topic.Topic', verbose_name='话题'),
        ),
        migrations.AddField(
            model_name='likeorcontra',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_or_contra', to='user.User', to_field='user', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='incognitocomment',
            name='topic_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incognito_comment', to='topic.Topic', verbose_name='话题'),
        ),
        migrations.AddField(
            model_name='comment',
            name='topic_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='topic.Topic', verbose_name='话题'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='user.User', to_field='user', verbose_name='用户'),
        ),
    ]

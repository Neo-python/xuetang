from user.models.model import User

from django.db import models
from tinymce.models import HTMLField


def upload_to_area(instance, filename):
    """生成唯一路径,返回路径.
    :param instance:
    :param filename:
    :return:
    """
    return 'static/img/' + instance._meta.verbose_name + '/' + instance.name + '.' + filename.split('.')[1]


class Area(models.Model):
    """板块分区模型
    """
    name = models.CharField(verbose_name='分区名', max_length=10, unique=True)
    path_name = models.CharField('url路径名', max_length=10, unique=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    icon_path = models.ImageField(
        verbose_name='图标路径', upload_to=upload_to_area)

    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'


class TopicStatus(models.Manager):
    def get_queryset(self):
        return super(TopicStatus, self).get_queryset().filter(status=True)


class Topic(models.Model):
    """话题模型
    """
    title = models.CharField(verbose_name='话题标题', max_length=50)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', verbose_name='用户',
                             default='AdminAudit')
    content = HTMLField('话题内容')
    area_id = models.ForeignKey(
        verbose_name='话题分区', to=Area, on_delete=models.CASCADE, related_name='topics')
    status = models.BooleanField(verbose_name='审核状态', default=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)
    fold_status = models.BooleanField(verbose_name='折叠状态', default=False)
    solve_status = models.BooleanField(verbose_name='话题终结状态', default=False)
    like = models.IntegerField(verbose_name='赞同数', default=0)
    contra = models.IntegerField(verbose_name='反对数', default=0)
    readings = models.IntegerField(verbose_name='阅读数', default=1)
    create_time = models.DateTimeField(verbose_name='发布时间', auto_now_add=True)
    modify_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    objects = models.Manager()
    status_true = TopicStatus()

    def __str__(self):
        return f'{self.title[:10]}... -- {self.user.user} -- {self.status}'


class Tag(models.Model):
    """标签模型
    """
    name = models.CharField(verbose_name='标签名', max_length=20)
    icon = models.FileField(
        verbose_name='图标', upload_to='status/img/tag/', default='/static/img/tag/default.png')
    description = models.TextField(verbose_name='描述', default='标签还没有描述...')
    status = models.BooleanField(verbose_name='状态', default=False)
    attention = models.IntegerField(verbose_name='关注数', default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.name} -- :{self.attention}'


class TopicAndTag(models.Model):
    """话题与标签关系模型
    """
    topic_id = models.ForeignKey(
        to=Topic, on_delete=models.CASCADE, related_name='tags', verbose_name='话题')
    tag_id = models.ForeignKey(
        to=Tag, on_delete=models.CASCADE, related_name='topics', verbose_name='标签')


class Comment(models.Model):
    """评论模型
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', related_name='comments',
                             verbose_name='用户')
    topic_id = models.ForeignKey(
        to=Topic, on_delete=models.CASCADE, related_name='comments', verbose_name='话题')
    reply_obj = models.ForeignKey(to='self', on_delete=models.CASCADE, verbose_name='回复对象', null=True,
                                  related_name='reply')
    content = HTMLField(verbose_name='评论内容')
    status = models.BooleanField(verbose_name='审核状态', default=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)
    ip = models.CharField(verbose_name='游客ip', max_length=48, null=True)
    time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)

    def __str__(self):
        return f'user:{self.user.user} topic:{self.topic_id.title[:10]} status:{self.status}'


class TouristsComment(models.Model):
    """游客评论待审核模型
    """
    topic_id = models.ForeignKey(to=Topic, on_delete=models.CASCADE, related_name='incognito_comment',
                                 verbose_name='话题')
    comment_obj = models.IntegerField(verbose_name='回复对象数据库id')
    content = models.CharField(verbose_name='评论内容', max_length=200)
    ip = models.CharField(verbose_name='游客ip', max_length=48)

    def __str__(self):
        return f'content:{self.content}'


class TopicLOC(models.Model):
    """话题点赞模型"""

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', related_name='like_or_contra',
                             verbose_name='用户')
    topic_id = models.ForeignKey(
        to=Topic, on_delete=models.CASCADE, related_name='like_or_contra', verbose_name='话题')
    status = models.NullBooleanField(verbose_name='赞或反对', null=True)

    def __str__(self):
        return f'{self.user.user} {self.topic_id.title[:10]} {self.status}'


class CommentLOC(models.Model):
    """comment Like or contra 评论点赞或反对模型"""

    cid = models.ForeignKey(
        to=Comment, on_delete=models.CASCADE, related_name='LOC')  # 评论id
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, to_field='user', related_name='commentLOC')  # 用户
    status = models.NullBooleanField(verbose_name='赞或反对', null=True)

    def __str__(self):
        return f'{self.id} {self.cid.id} {self.status}'


class Collection(models.Model):
    """收藏模型"""

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, to_field='user', related_name='collections',
                             verbose_name='用户')
    topic_id = models.ForeignKey(
        to=Topic, on_delete=models.CASCADE, related_name='collections', verbose_name='话题')

    def __str__(self):
        return f'{self.user.user} : {self.topic_id.title}'

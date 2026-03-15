from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """用户模型，扩展默认User模型"""
    # 基本信息
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(max_length=500, null=True, blank=True, verbose_name='个人简介')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    
    # 积分和等级系统
    points = models.IntegerField(default=0, verbose_name='积分')
    experience = models.IntegerField(default=0, verbose_name='经验值')
    level = models.IntegerField(default=1, verbose_name='等级')
    
    # 签到相关
    last_checkin = models.DateField(null=True, blank=True, verbose_name='最后签到时间')
    checkin_streak = models.IntegerField(default=0, verbose_name='连续签到天数')
    
    # AI使用次数
    daily_ai_uses = models.IntegerField(default=0, verbose_name='今日AI使用次数')
    last_ai_reset = models.DateField(default=timezone.now, verbose_name='AI次数重置时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

class PointTransaction(models.Model):
    """积分交易记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    amount = models.IntegerField(verbose_name='积分数量')  # 正数为获得，负数为消耗
    type = models.CharField(max_length=50, verbose_name='交易类型')  # 签到、发帖、评论、AI使用、商城兑换等
    description = models.CharField(max_length=200, verbose_name='交易描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='交易时间')
    
    class Meta:
        verbose_name = '积分交易'
        verbose_name_plural = '积分交易'
        ordering = ['-created_at']

from django.db import models
from users.models import User
from django.utils import timezone
import uuid



class Category(models.Model):
    """分类模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(max_length=200, null=True, blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

class Article(models.Model):
    """篮球资讯文章模型"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='分类')
    cover_image = models.ImageField(upload_to='articles/', null=True, blank=True, verbose_name='封面图片')
    view_count = models.IntegerField(default=0, verbose_name='浏览量')
    is_published = models.BooleanField(default=False, verbose_name='是否发布')
    is_essence = models.BooleanField(default=False, verbose_name='是否加精')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '篮球资讯'
        verbose_name_plural = '篮球资讯'
        ordering = ['-created_at']

class Post(models.Model):
    """用户论坛帖子模型"""
    MODERATION_STATUS_CHOICES = [
        ("pending", "待审核"),
        ("approved", "已通过"),
        ("rejected", "已拒绝"),
    ]
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='分类')
    cover_image = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name='封面图片')
    images = models.JSONField(default=list, verbose_name='图片列表')
    tags = models.JSONField(default=list, verbose_name='话题标签')
    view_count = models.IntegerField(default=0, verbose_name='浏览量')
    comment_count = models.IntegerField(default=0, verbose_name='评论数')
    is_published = models.BooleanField(default=False, verbose_name='是否发布')
    is_essence = models.BooleanField(default=False, verbose_name='是否加精')
    moderation_status = models.CharField(max_length=20, choices=MODERATION_STATUS_CHOICES, default='pending', verbose_name='审核状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '论坛帖子'
        verbose_name_plural = '论坛帖子'
        ordering = ['-created_at']

class Comment(models.Model):
    """评论模型"""
    content = models.TextField(verbose_name='评论内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论用户', related_name='comments', null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='所属帖子', related_name='comments', null=True, blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='父评论')
    is_published = models.BooleanField(default=True, verbose_name='是否发布')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

class PostView(models.Model):
    """帖子浏览记录模型 - 用于记录用户浏览过的帖子"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='帖子')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='浏览时间')
    
    class Meta:
        verbose_name = '帖子浏览记录'
        verbose_name_plural = '帖子浏览记录'
        unique_together = ['user', 'post']  # 每个用户对每个帖子只能有一条记录
        ordering = ['-created_at']

class Player(models.Model):
    """球员模型"""
    name = models.CharField(max_length=100, verbose_name='球员姓名')
    team = models.CharField(max_length=100, default='', verbose_name='所属球队')
    position = models.CharField(max_length=50, default='', verbose_name='位置')
    jersey_number = models.IntegerField(null=True, blank=True, verbose_name='球衣号码')
    country = models.CharField(max_length=50, default='中国', verbose_name='国籍')
    height = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name='身高(米)')
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name='体重(公斤)')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    avatar = models.ImageField(upload_to='players/', null=True, blank=True, verbose_name='球员头像')
    description = models.TextField(null=True, blank=True, verbose_name='球员描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '球员'
        verbose_name_plural = '球员'

class PlayerRating(models.Model):
    """球员评分模型"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='球员')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评分用户')
    rating = models.IntegerField(verbose_name='评分(1-5星)')
    comment = models.TextField(null=True, blank=True, verbose_name='评分评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评分时间')
    
    class Meta:
        verbose_name = '球员评分'
        verbose_name_plural = '球员评分'
        unique_together = ['player', 'user']  # 每个用户对每个球员只能评分一次

class AIChat(models.Model):
    """AI聊天记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    question = models.TextField(verbose_name='问题')
    answer = models.TextField(verbose_name='回答')
    is_free = models.BooleanField(default=True, verbose_name='是否免费')
    points_consumed = models.IntegerField(default=0, verbose_name='消耗积分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='聊天时间')
    
    class Meta:
        verbose_name = 'AI聊天记录'
        verbose_name_plural = 'AI聊天记录'
        ordering = ['-created_at']

class TrainingPlan(models.Model):
    """训练计划模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='计划标题')
    description = models.TextField(verbose_name='计划描述')
    duration_days = models.IntegerField(verbose_name='计划天数')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '训练计划'
        verbose_name_plural = '训练计划'

class TrainingDay(models.Model):
    """训练日模型"""
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, verbose_name='训练计划')
    day_number = models.IntegerField(verbose_name='第几天')
    exercises = models.TextField(verbose_name='训练内容')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')
    completed = models.BooleanField(default=False, verbose_name='是否完成')
    
    class Meta:
        verbose_name = '训练日'
        verbose_name_plural = '训练日'
        unique_together = ['plan', 'day_number']


class Game(models.Model):
    """篮球比赛基础信息，用于首页展示比分（如 NBA、CBA 等）"""

    LEAGUE_CHOICES = [
        ("NBA", "NBA"),
        ("CBA", "CBA"),
        ("OTHER", "其他联赛"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "未开始"),
        ("live", "进行中"),
        ("finished", "已结束"),
    ]

    league = models.CharField(max_length=20, choices=LEAGUE_CHOICES, default="NBA")
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    start_time = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=64, blank=True)
    external_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self) -> str:
        return f"{self.league} {self.home_team} vs {self.away_team}"


class News(models.Model):
    """篮球资讯（官方新闻、平台资讯等），展示在资讯流中"""

    SOURCE_CHOICES = [
        ("official", "官方"),
        ("media", "媒体"),
        ("community", "社区精选"),
    ]

    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="media")
    source_name = models.CharField(max_length=100, blank=True)
    external_url = models.URLField(blank=True)
    cover_image = models.URLField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title





# 商城相关模型
class ProductCategory(models.Model):
    """商品分类模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(max_length=200, null=True, blank=True, verbose_name='分类描述')
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='父分类')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'

class Product(models.Model):
    """商品模型"""
    name = models.CharField(max_length=200, verbose_name='商品名称')
    description = models.TextField(verbose_name='商品描述')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, verbose_name='商品分类')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    points_price = models.IntegerField(null=True, blank=True, verbose_name='积分价格')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    is_course = models.BooleanField(default=False, verbose_name='是否为课程')
    video_url = models.URLField(null=True, blank=True, verbose_name='课程视频链接')
    cover_image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='商品封面')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'

class ProductImage(models.Model):
    """商品图片模型"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    image = models.ImageField(upload_to='product_images/', verbose_name='图片')
    is_main = models.BooleanField(default=False, verbose_name='是否为主图')
    
    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = '商品图片'

class Cart(models.Model):
    """购物车模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.IntegerField(default=1, verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        unique_together = ['user', 'product']

class Order(models.Model):
    """订单模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    order_number = models.CharField(max_length=50, unique=True, default='TEMP_ORDER', verbose_name='订单号')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name='订单总金额')
    total_points = models.IntegerField(default=0, verbose_name='使用积分')
    status = models.CharField(max_length=20, default='待支付', verbose_name='订单状态')  # 待支付、已支付、已发货、已完成、已取消
    payment_method = models.CharField(max_length=20, null=True, blank=True, verbose_name='支付方式')
    shipping_address = models.TextField(null=True, blank=True, verbose_name='收货地址')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='联系电话')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

class OrderItem(models.Model):
    """订单商品项模型"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.IntegerField(default=1, verbose_name='数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name='单价')
    points_used = models.IntegerField(default=0, verbose_name='使用积分')
    
    class Meta:
        verbose_name = '订单商品项'
        verbose_name_plural = '订单商品项'

class Address(models.Model):
    """用户地址模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(max_length=50, verbose_name='收货人')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    province = models.CharField(max_length=50, verbose_name='省份')
    city = models.CharField(max_length=50, verbose_name='城市')
    district = models.CharField(max_length=50, verbose_name='区县')
    detail_address = models.TextField(verbose_name='详细地址')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = '收货地址'


class CoachSession(models.Model):
    """AI 篮球教练对话记录（后续接入大模型/Agent）"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="coach_sessions", null=True, blank=True
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Coach session #{self.id}"


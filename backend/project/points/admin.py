from django.contrib import admin
from .models import Post, Category, Article, Comment, PostView, Player, PlayerRating, AIChat, TrainingPlan, TrainingDay, Game, News, ProductCategory, Product, ProductImage, Cart, Order, OrderItem, Address

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'moderation_status', 'is_published', 'is_essence', 'view_count', 'comment_count', 'created_at')
    list_filter = ('moderation_status', 'is_published', 'is_essence', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    list_editable = ('moderation_status', 'is_published', 'is_essence')
    readonly_fields = ('view_count', 'comment_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'is_essence', 'view_count', 'created_at')
    list_filter = ('is_published', 'is_essence', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    list_editable = ('is_published', 'is_essence')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'post', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('content', 'author__username', 'post__title')
    list_editable = ('is_published',)

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__title')
    readonly_fields = ('user', 'post', 'created_at')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'position', 'jersey_number', 'country', 'height', 'weight')
    list_filter = ('team', 'position', 'country')
    search_fields = ('name', 'team')

@admin.register(PlayerRating)
class PlayerRatingAdmin(admin.ModelAdmin):
    list_display = ('player', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('player__name', 'user__username')

@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_free', 'points_consumed', 'created_at')
    list_filter = ('is_free', 'created_at')
    search_fields = ('question', 'answer', 'user__username')

@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'duration_days', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'user__username')

@admin.register(TrainingDay)
class TrainingDayAdmin(admin.ModelAdmin):
    list_display = ('plan', 'day_number', 'completed')
    list_filter = ('completed',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('league', 'home_team', 'away_team', 'home_score', 'away_score', 'status', 'start_time')
    list_filter = ('league', 'status', 'start_time')
    search_fields = ('home_team', 'away_team')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'source_name', 'published_at', 'created_at')
    list_filter = ('source', 'published_at', 'created_at')
    search_fields = ('title', 'summary', 'source_name')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'points_price', 'stock', 'sales', 'is_active', 'is_course')
    list_filter = ('is_active', 'is_course', 'category', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'stock')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_main')
    list_filter = ('is_main',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'total_points', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'phone')
    list_editable = ('status',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'points_used')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'province', 'city', 'district', 'is_default', 'created_at')
    list_filter = ('province', 'city', 'is_default', 'created_at')
    search_fields = ('name', 'phone', 'user__username')
    list_editable = ('is_default',)

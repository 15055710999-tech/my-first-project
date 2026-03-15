from django.urls import path
from . import views


urlpatterns = [
    # 篮球资讯 & 社区
    path("feed/", views.feed, name="basketball_feed"),
    path("posts/", views.post_list_create, name="post_list_create"),
    path("posts/my/", views.my_posts, name="my_posts"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/<int:post_id>/comment/", views.post_comment, name="post_comment"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),

    # 比赛比分
    path("games/", views.game_list, name="game_list"),

    # 球员评分
    path("players/", views.player_list, name="player_list"),
    path("players/<int:player_id>/rate/", views.player_rate, name="player_rate"),

    # 商城
    path("shop/products/", views.product_list, name="product_list"),
    path("shop/orders/", views.order_create, name="order_create"),

    # AI 篮球教练
    path("coach/ask/", views.coach_ask, name="coach_ask"),
]


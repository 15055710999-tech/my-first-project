import json
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from typing import Union, Optional

from .models import (
    Game,
    News,
    Post,
    Comment,
    PostView,
    Player,
    PlayerRating,
    Product,
    Order,
    OrderItem,
    CoachSession,
)

User = get_user_model()


def _user_from_request(request: HttpRequest):
    """非常简化的鉴权：根据用户名获取用户，仅用于演示。
    实际项目建议使用 JWT / session 等更安全的方案。
    """
    username = request.headers.get("X-USER") or request.GET.get("username")
    
    # 添加调试日志
    print(f"调试信息 - 请求头: {dict(request.headers)}")
    print(f"调试信息 - 用户名: {username}")
    
    if not username:
        return None
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def game_list(request: HttpRequest):
    """获取比赛列表（示例中若数据库为空，会返回几条假数据）"""
    if Game.objects.count() == 0:
        sample_games = [
            {
                "league": "NBA",
                "home_team": "Lakers",
                "away_team": "Warriors",
                "home_score": 102,
                "away_score": 99,
                "status": "finished",
                "external_url": "https://www.nba.com",
            },
            {
                "league": "NBA",
                "home_team": "Celtics",
                "away_team": "Bucks",
                "home_score": 88,
                "away_score": 90,
                "status": "finished",
                "external_url": "https://www.nba.com",
            },
        ]
        return JsonResponse({"code": 200, "data": sample_games})

    data = [
        {
            "id": g.id,
            "league": g.league,
            "home_team": g.home_team,
            "away_team": g.away_team,
            "home_score": g.home_score,
            "away_score": g.away_score,
            "status": g.status,
            "start_time": g.start_time,
            "external_url": g.external_url,
        }
        for g in Game.objects.all()[:20]
    ]
    return JsonResponse({"code": 200, "data": data})


def feed(request: HttpRequest):
    """首页资讯流：比赛 + 官方新闻 + 用户帖子摘要"""
    # 比赛
    games_resp = game_list(request)
    games_data = json.loads(games_resp.content.decode("utf-8")).get("data", [])

    # 官方新闻（若为空，返回几条示例）
    if News.objects.count() == 0:
        news_list = [
            {
                "title": "NBA 总决赛即将开打",
                "summary": "本赛季总决赛即将打响，两队状态火热，敬请期待。",
                "source": "media",
                "source_name": "示例体育",
                "external_url": "https://www.nba.com",
            },
            {
                "title": "某某球员完成大三元",
                "summary": "他在比赛中砍下 30 分 12 篮板 10 助攻，状态爆棚。",
                "source": "media",
                "source_name": "示例体育",
                "external_url": "https://www.nba.com",
            },
        ]
    else:
        news_list = [
            {
                "id": n.id,
                "title": n.title,
                "summary": n.summary,
                "source": n.source,
                "source_name": n.source_name,
                "external_url": n.external_url,
                "cover_image": n.cover_image,
                "published_at": n.published_at,
            }
            for n in News.objects.all()[:20]
        ]

    # 用户帖子（只取部分字段）
    posts = [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content[:100] + ("..." if len(p.content) > 100 else ""),
            "author": p.author.username if p.author else "匿名",
            "view_count": p.view_count,
            "comment_count": p.comment_count,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
            "is_published": p.is_published,
            "is_essence": p.is_essence,
        }
        for p in Post.objects.filter(is_published=True)[:20]
    ]

    return JsonResponse(
        {
            "code": 200,
            "data": {
                "games": games_data,
                "news": news_list,
                "posts": posts,
            },
        }
    )


@csrf_exempt
def post_list_create(request: HttpRequest):
    """帖子列表 + 发表帖子"""
    if request.method == "GET":
        # 只返回审核通过且已发布的帖子
        posts = Post.objects.filter(moderation_status='approved', is_published=True)
        data = [
            {
                "id": p.id,
                "title": p.title,
                "content": p.content,
                "author": p.author.username if p.author else "匿名",
                "cover_image": p.cover_image.url if p.cover_image else None,
                "images": p.images if p.images else [],
                "tags": p.tags if p.tags else [],
                "view_count": p.view_count,
                "comment_count": p.comment_count,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
                "is_essence": p.is_essence,
                "moderation_status": p.moderation_status,
            }
            for p in posts
        ]
        return JsonResponse({"code": 200, "data": data})

    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code": 400, "message": "请求体必须为 JSON"}, status=400)

        user = _user_from_request(request)
        if user is None:
            # 尝试从 payload 里获取用户名
            username = payload.get("username")
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({"code": 401, "message": "用户不存在，请先登录"}, status=401)
            else:
                return JsonResponse({"code": 401, "message": "缺少用户信息，请先登录"}, status=401)

        title = payload.get("title", "").strip()
        content = payload.get("content", "").strip()
        images = payload.get("images", [])
        tags = payload.get("tags", [])
        
        if not title or not content:
            return JsonResponse({"code": 400, "message": "标题和内容不能为空"}, status=400)

        post = Post.objects.create(
            author=user,
            title=title,
            content=content,
            images=images,
            tags=tags,
            moderation_status='pending',  # 默认为待审核状态
            is_published=False,  # 新帖子默认为未发布，需要管理员审核后发布
        )
        return JsonResponse(
            {
                "code": 200,
                "message": "发帖成功，等待管理员审核",
                "data": {"id": post.id, "title": post.title},
            }
        )


@csrf_exempt
def post_detail(request: HttpRequest, post_id: int):
    """帖子详情 - 每个用户只增加一次浏览量"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"code": 404, "message": "帖子不存在"}, status=404)

    # 获取当前用户
    user = _user_from_request(request)
    
    # 如果用户已登录，检查是否浏览过该帖子
    if user:
        # 使用 get_or_create 来检查是否已存在浏览记录
        view_record, created = PostView.objects.get_or_create(
            user=user,
            post=post
        )
        # 如果是新创建的浏览记录，增加浏览量
        if created:
            post.view_count += 1
            post.save(update_fields=['view_count'])
    else:
        # 未登录用户不增加浏览量（或可以选择增加）
        pass

    # 获取已发布的评论列表
    comments = Comment.objects.filter(post=post, is_published=True).order_by('-created_at')
    comments_data = [
        {
            "id": c.id,
            "content": c.content,
            "author": c.author.username if c.author else "匿名",
            "author_id": c.author.id if c.author else None,
            "parent_comment_id": c.parent_comment.id if c.parent_comment else None,
            "parent_comment_author": c.parent_comment.author.username if c.parent_comment and c.parent_comment.author else None,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
        }
        for c in comments
    ]

    data = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author.username if post.author else "匿名",
        "author_id": post.author.id if post.author else None,
        "view_count": post.view_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
        "is_published": post.is_published,
        "is_essence": post.is_essence,
        "comments": comments_data,
    }
    return JsonResponse({"code": 200, "data": data})


@csrf_exempt
def post_comment(request: HttpRequest, post_id: int):
    """发表评论或回复评论"""
    if request.method != "POST":
        return JsonResponse({"code": 405, "message": "仅支持 POST 请求"}, status=405)

    user = _user_from_request(request)
    if user is None:
        return JsonResponse({"code": 401, "message": "未登录"}, status=401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"code": 404, "message": "帖子不存在"}, status=404)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "请求体必须是JSON格式"}, status=400)

    content = payload.get("content", "").strip()
    if not content:
        return JsonResponse({"code": 400, "message": "评论内容不能为空"}, status=400)
    
    parent_comment_id = payload.get("parent_comment_id", None)
    parent_comment = None
    if parent_comment_id:
        try:
            parent_comment = Comment.objects.get(id=parent_comment_id, post=post)
        except Comment.DoesNotExist:
            return JsonResponse({"code": 404, "message": "要回复的评论不存在"}, status=404)

    # 创建评论，自动设置为已发布
    comment = Comment.objects.create(
        post=post,
        author=user,
        content=content,
        parent_comment=parent_comment,
        is_published=True,
    )

    # 更新帖子评论数
    post.comment_count += 1
    post.save(update_fields=['comment_count'])

    return JsonResponse({
        "code": 200,
        "message": "评论成功",
        "data": {
            "id": comment.id,
            "content": comment.content,
            "author": comment.author.username,
            "author_id": comment.author.id,
            "parent_comment_id": comment.parent_comment.id if comment.parent_comment else None,
            "parent_comment_author": comment.parent_comment.author.username if comment.parent_comment and comment.parent_comment.author else None,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
    })


@csrf_exempt
def post_delete(request: HttpRequest, post_id: int):
    """删除帖子 - 只有作者可以删除自己的帖子，管理员不能删除用户帖子"""
    if request.method != "DELETE" and request.method != "POST":
        return JsonResponse({"code": 405, "message": "仅支持 DELETE 或 POST 请求"}, status=405)

    user = _user_from_request(request)
    if user is None:
        return JsonResponse({"code": 401, "message": "未登录"}, status=401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"code": 404, "message": "帖子不存在"}, status=404)

    # 检查权限：只有作者本人可以删除自己的帖子，管理员不能删除用户帖子
    is_author = post.author and post.author.id == user.id

    if not is_author:
        return JsonResponse({"code": 403, "message": "只能删除自己发布的帖子"}, status=403)

    # 彻底删除帖子（从数据库中删除）
    post.delete()
    return JsonResponse({"code": 200, "message": "帖子删除成功"})


@csrf_exempt
def comment_delete(request: HttpRequest, comment_id: int):
    """删除评论 - 贴主可以删除所有评论，其他人只能删除自己的"""
    if request.method != "DELETE" and request.method != "POST":
        return JsonResponse({"code": 405, "message": "仅支持 DELETE 或 POST 请求"}, status=405)

    user = _user_from_request(request)
    if user is None:
        return JsonResponse({"code": 401, "message": "未登录"}, status=401)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"code": 404, "message": "评论不存在"}, status=404)

    # 检查权限
    is_comment_author = comment.author and comment.author.id == user.id
    is_post_author = comment.post and comment.post.author and comment.post.author.id == user.id

    if not is_comment_author and not is_post_author:
        return JsonResponse({"code": 403, "message": "只能删除自己的评论或自己帖子下的评论"}, status=403)

    # 更新帖子评论数
    if comment.post:
        comment.post.comment_count -= 1
        if comment.post.comment_count < 0:
            comment.post.comment_count = 0
        comment.post.save(update_fields=['comment_count'])

    # 彻底删除评论
    comment.delete()
    return JsonResponse({"code": 200, "message": "评论删除成功"})


@csrf_exempt
def my_posts(request: HttpRequest):
    """获取当前用户的所有帖子（包括待审核、已拒绝、已通过）"""
    if request.method != "GET":
        return JsonResponse({"code": 405, "message": "仅支持 GET 请求"}, status=405)

    user = _user_from_request(request)
    if user is None:
        return JsonResponse({"code": 401, "message": "未登录"}, status=401)

    # 获取该用户的所有帖子（包括所有审核状态）
    posts = Post.objects.filter(author=user).order_by('-created_at')
    data = [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "author": p.author.username if p.author else "匿名",
            "author_id": p.author.id if p.author else None,
            "cover_image": p.cover_image.url if p.cover_image else None,
            "images": p.images if p.images else [],
            "tags": p.tags if p.tags else [],
            "view_count": p.view_count,
            "comment_count": p.comment_count,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
            "is_essence": p.is_essence,
            "is_published": p.is_published,
            "moderation_status": p.moderation_status,
            "moderation_status_display": p.get_moderation_status_display(),
        }
        for p in posts
    ]
    return JsonResponse({"code": 200, "data": data})


def player_list(request: HttpRequest):
    """球员列表"""
    players = Player.objects.all()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "team": p.team,
            "position": p.position,
            "jersey_number": p.jersey_number,
            "avatar": p.avatar.url if p.avatar else None,
            "rating_avg": PlayerRating.objects.filter(player=p).aggregate(Avg("rating"))["rating__avg"] or 0,
        }
        for p in players
    ]
    return JsonResponse({"code": 200, "data": data})


@csrf_exempt
def player_rate(request: HttpRequest, player_id: int):
    """球员评分"""
    if request.method != "POST":
        return JsonResponse({"code": 405, "message": "仅支持 POST 请求"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "请求体必须为 JSON"}, status=400)

    user = _user_from_request(request)
    if user is None:
        return JsonResponse({"code": 401, "message": "未登录"}, status=401)

    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return JsonResponse({"code": 404, "message": "球员不存在"}, status=404)

    rating_value = payload.get("score")
    comment = payload.get("comment", "")

    if rating_value is None or not (1 <= int(rating_value) <= 5):
        return JsonResponse({"code": 400, "message": "评分必须在 1-5 之间"}, status=400)

    # 更新或创建评分
    PlayerRating.objects.update_or_create(
        player=player,
        user=user,
        defaults={"rating": rating_value, "comment": comment},
    )

    return JsonResponse({"code": 200, "message": "评分成功"})


def product_list(request: HttpRequest):
    """商品列表"""
    products = Product.objects.filter(is_active=True)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": str(p.price),
            "points_price": p.points_price,
            "stock": p.stock,
            "cover_image": p.cover_image.url if p.cover_image else None,
            "is_course": p.is_course,
        }
        for p in products
    ]
    return JsonResponse({"code": 200, "data": data})


@csrf_exempt
def order_create(request: HttpRequest):
    """创建订单"""
    if request.method != "POST":
        return JsonResponse({"code": 405, "message": "仅支持 POST 请求"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "请求体必须为 JSON"}, status=400)

    user = _user_from_request(request)
    if user is None:
        return JsonResponse({"code": 401, "message": "未登录"}, status=401)

    items = payload.get("items", [])
    if not items:
        return JsonResponse({"code": 400, "message": "订单商品不能为空"}, status=400)

    # 简化：直接创建订单
    order = Order.objects.create(
        user=user,
        order_number=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        status="待支付",
    )

    total_amount = 0
    for item in items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)
        try:
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )
            total_amount += float(product.price) * quantity
        except Product.DoesNotExist:
            continue

    order.total_amount = total_amount
    order.save()

    return JsonResponse({"code": 200, "message": "订单创建成功", "data": {"order_id": order.id}})


@csrf_exempt
def coach_ask(request: HttpRequest):
    """AI 篮球教练问答"""
    if request.method != "POST":
        return JsonResponse({"code": 405, "message": "仅支持 POST 请求"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "请求体必须为 JSON"}, status=400)

    user = _user_from_request(request)
    question = payload.get("question", "").strip()

    if not question:
        return JsonResponse({"code": 400, "message": "问题不能为空"}, status=400)

    # 简化：模拟 AI 回答
    answer = f"关于'{question}'，建议多练习基本功，保持良好的投篮姿势。"

    if user:
        session = CoachSession.objects.create(
            user=user,
            question=question,
            answer=answer,
        )
    else:
        session = None

    return JsonResponse(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "session_id": session.id if session else None,
                "question": question,
                "answer": answer,
                "created_at": session.created_at if session else None,
            },
        }
    )

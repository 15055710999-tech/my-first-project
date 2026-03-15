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
        posts = Post.objects.all()
        data = [
            {
                "id": p.id,
                "title": p.title,
                "content": p.content,
                "author": p.author.username if p.author else "匿名",
                "view_count": p.view_count,
                "comment_count": p.comment_count,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
                "is_published": p.is_published,
                "is_essence": p.is_essence,
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
            # 简化：也允许通过 payload 里指定用户名创建，方便前后端联调
            username = payload.get("username")
            if username:
                user, _ = User.objects.get_or_create(username=username)
            else:
                return JsonResponse({"code": 401, "message": "缺少用户信息"}, status=401)

        title = payload.get("title", "").strip()
        content = payload.get("content", "").strip()
        if not title or not content:
            return JsonResponse({"code": 400, "message": "标题和内容不能为空"}, status=400)

        post = Post.objects.create(
            author=user,
            title=title,
            content=content,
            # 默认 pending，可在后台管理里做人工审核
        )
        return JsonResponse(
            {
                "code": 200,
                "message": "发帖成功，等待审核",
                "data": {"id": post.id, "title": post.title},
            }
        )

    return JsonResponse({"code": 405, "message": "Method not allowed"}, status=405)


def post_detail(request: HttpRequest, post_id: int):
    """帖子详情"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"code": 404, "message": "帖子不存在"}, status=404)

    data = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author.username if post.author else "匿名",
        "view_count": post.view_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
        "is_published": post.is_published,
        "is_essence": post.is_essence,
    }
    return JsonResponse({"code": 200, "data": data})


def player_list(request: HttpRequest):
    """球员列表，包含系统评分 + 用户平均评分"""
    # 若没有任何球员，返回一些示例数据方便前端展示
    if Player.objects.count() == 0:
        sample_players = [
            {
                "name": "LeBron James",
                "nickname": "老詹",
                "team": "Lakers",
                "position": "SF",
                "is_professional": True,
                "is_influencer": False,
                "system_score": 9.5,
                "average_user_score": 9.2,
                "description": "全能前锋，生涯多次总冠军。",
            },
            {
                "name": "Curry",
                "nickname": "库里",
                "team": "Warriors",
                "position": "PG",
                "is_professional": True,
                "is_influencer": False,
                "system_score": 9.4,
                "average_user_score": 9.3,
                "description": "三分射手，改变了篮球打法。",
            },
        ]
        return JsonResponse({"code": 200, "data": sample_players})

    players = Player.objects.all().annotate(avg_user_score=Avg("ratings__score"))
    data = [
        {
            "id": p.id,
            "name": p.name,
            "nickname": p.nickname,
            "team": p.team,
            "position": p.position,
            "is_professional": p.is_professional,
            "is_influencer": p.is_influencer,
            "avatar_url": p.avatar_url,
            "description": p.description,
            "system_score": p.system_score,
            "average_user_score": p.avg_user_score or 0.0,
        }
        for p in players
    ]
    return JsonResponse({"code": 200, "data": data})


@csrf_exempt
def player_rate(request: HttpRequest, player_id: int):
    """给球员打分"""
    if request.method != "POST":
        return JsonResponse({"code": 405, "message": "Method not allowed"}, status=405)

    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return JsonResponse({"code": 404, "message": "球员不存在"}, status=404)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "请求体必须为 JSON"}, status=400)

    user = _user_from_request(request)
    if user is None:
        username = payload.get("username")
        if username:
            user, _ = User.objects.get_or_create(username=username)
        else:
            return JsonResponse({"code": 401, "message": "缺少用户信息"}, status=401)

    score = int(payload.get("score", 0))
    comment = payload.get("comment", "").strip()
    if score < 1 or score > 10:
        return JsonResponse({"code": 400, "message": "评分必须在 1~10 之间"}, status=400)

    rating, created = PlayerRating.objects.update_or_create(
        player=player,
        user=user,
        defaults={"score": score, "comment": comment},
    )
    return JsonResponse(
        {
            "code": 200,
            "message": "评分成功" if created else "评分已更新",
            "data": {
                "player_id": player.id,
                "user": user.username,
                "score": rating.score,
                "comment": rating.comment,
            },
        }
    )


def product_list(request: HttpRequest):
    """商品列表（篮球装备 / 课程），若为空则返回示例数据"""
    if Product.objects.count() == 0:
        sample_products = [
            {
                "name": "专业比赛用篮球",
                "category": "gear",
                "description": "适合室内外比赛，手感出色。",
                "price": "399.00",
                "image_url": "",
            },
            {
                "name": "三分专项训练课程",
                "category": "course",
                "description": "从脚步到出手，系统提升三分命中率。",
                "price": "199.00",
                "image_url": "",
            },
        ]
        return JsonResponse({"code": 200, "data": sample_products})

    products = Product.objects.filter(is_active=True)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "price": str(p.price),
            "inventory": p.inventory,
            "image_url": p.image_url,
        }
        for p in products
    ]
    return JsonResponse({"code": 200, "data": data})


@csrf_exempt
def order_create(request: HttpRequest):
    """创建订单（非常简化版），只用于演示下单流程"""
    if request.method != "POST":
        return JsonResponse({"code": 405, "message": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "请求体必须为 JSON"}, status=400)

    user = _user_from_request(request)
    if user is None:
        username = payload.get("username")
        if username:
            user, _ = User.objects.get_or_create(username=username)
        else:
            return JsonResponse({"code": 401, "message": "缺少用户信息"}, status=401)

    items = payload.get("items", [])
    if not items:
        return JsonResponse({"code": 400, "message": "订单商品不能为空"}, status=400)

    # 这里的价格计算都在后端完成，前端只需要传 product_id 和数量
    order = Order.objects.create(user=user, status="created", total_price=0)
    total_price = 0
    for item in items:
        product_id = item.get("product_id")
        quantity = int(item.get("quantity", 1))
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            continue
        unit_price = product.price
        total_price += unit_price * quantity
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
        )

    order.total_price = total_price
    order.save()

    return JsonResponse(
        {
            "code": 200,
            "message": "订单创建成功",
            "data": {
                "order_id": order.id,
                "total_price": str(order.total_price),
                "status": order.status,
            },
        }
    )


@csrf_exempt
def coach_ask(request: HttpRequest):
    """AI 篮球教练接口（当前为占位实现，后续可接入大模型/Agent）"""
    if request.method != "POST":
        return JsonResponse({"code": 405, "message": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "message": "请求体必须为 JSON"}, status=400)

    question = payload.get("question", "").strip()
    if not question:
        return JsonResponse({"code": 400, "message": "问题不能为空"}, status=400)

    user = _user_from_request(request)
    username = user.username if user else "篮球爱好者"

    # 这里是一个非常简单的“智能回答”，主要用于演示接口流程
    answer = (
        f"{username}，关于你提到的训练问题：“{question}”，"
        "目前建议从基础运球、脚步启动和投篮手型三个方面入手，"
        "保持每周 3~4 次针对性训练，并结合视频回放进行自我纠正。"
        "后续可以接入大模型，为你生成更个性化的训练计划和课程推荐。"
    )

    session = CoachSession.objects.create(
        user=user,
        question=question,
        answer=answer,
    )

    return JsonResponse(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "session_id": session.id,
                "question": question,
                "answer": answer,
                "created_at": session.created_at,
            },
        }
    )


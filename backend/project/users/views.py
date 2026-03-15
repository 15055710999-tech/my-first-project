from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

User = get_user_model()

@csrf_exempt
def register(request):
    """用户注册"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            
            # 检查用户是否已存在
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'code': 400,
                    'message': '用户名已存在'
                }, status=400)
            
            # 创建用户
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            
            return JsonResponse({
                'code': 200,
                'message': '注册成功',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'points_balance': 10  # 注册送10积分
                    },
                    'token': 'test_token_123'  # 简化版，实际应该用JWT
                }
            })
        except Exception as e:
            return JsonResponse({
                'code': 400,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'code': 405,
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
def login(request):
    """用户登录"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            # 验证用户
            user = authenticate(username=username, password=password)
            
            if user is not None:
                return JsonResponse({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'points_balance': 100  # 示例积分
                        },
                        'token': 'test_token_123'
                    }
                })
            else:
                return JsonResponse({
                    'code': 400,
                    'message': '用户名或密码错误'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'code': 400,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'code': 405,
        'message': 'Method not allowed'
    }, status=405)

def profile(request):
    """获取用户资料（需要登录）"""
    # 简单版本，返回提示信息
    return JsonResponse({
        'code': 200,
        'message': '请先登录',
        'data': {
            'user': None
        }
    })

# 如果需要完整的profile功能，可以使用这个版本
# @login_required
# def profile_detail(request):
#     """获取当前登录用户的详细资料"""
#     user = request.user
#     return JsonResponse({
#         'code': 200,
#         'data': {
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#             'last_login': user.last_login,
#             'date_joined': user.date_joined
#         }
#     })
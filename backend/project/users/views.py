from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64
import os
from datetime import datetime

User = get_user_model()

def _user_from_request(request: HttpRequest):
    """从请求中获取用户"""
    username = request.headers.get("X-USER") or request.GET.get("username")
    if not username:
        return None
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None

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
                            'avatar': user.avatar.url if user.avatar else None,
                            'points_balance': user.points,
                            'level': user.level,
                            'phone': user.phone,
                            'gender': user.gender,
                            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                            'bio': user.bio
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

@csrf_exempt
def get_user_info(request):
    """获取用户信息"""
    user = _user_from_request(request)
    if not user:
        return JsonResponse({
            'code': 401,
            'message': '未登录'
        }, status=401)
    
    return JsonResponse({
        'code': 200,
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar.url if user.avatar else None,
            'points': user.points,
            'level': user.level,
            'phone': user.phone,
            'gender': user.gender,
            'birth_date': user.birth_date.isoformat() if user.birth_date else None,
            'bio': user.bio
        }
    })

@csrf_exempt
def update_profile(request):
    """更新个人信息"""
    if request.method != 'PUT':
        return JsonResponse({
            'code': 405,
            'message': 'Method not allowed'
        }, status=405)
    
    user = _user_from_request(request)
    if not user:
        return JsonResponse({
            'code': 401,
            'message': '未登录'
        }, status=401)
    
    try:
        data = json.loads(request.body)
        errors = {}
        
        # 检查用户名是否重复
        username = data.get('username')
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                errors['username'] = '用户名已存在'
            else:
                user.username = username
        
        # 检查邮箱
        email = data.get('email')
        if email:
            user.email = email
        
        # 其他字段
        user.phone = data.get('phone', user.phone)
        user.gender = data.get('gender', user.gender)
        user.bio = data.get('bio', user.bio)
        
        # 处理出生日期
        birth_date = data.get('birth_date')
        if birth_date:
            try:
                # 前端以 'YYYY-MM-DD' 形式传递，转换为 date 对象
                user.birth_date = datetime.fromisoformat(birth_date).date()
            except ValueError:
                errors['birth_date'] = '出生日期格式不正确，应为 YYYY-MM-DD'
        
        if errors:
            return JsonResponse({
                'code': 400,
                'message': '更新失败',
                'data': errors
            }, status=400)
        
        user.save()
        
        return JsonResponse({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'gender': user.gender,
                'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                'bio': user.bio
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'code': 400,
            'message': str(e)
        }, status=400)

@csrf_exempt
def change_password(request):
    """修改密码"""
    if request.method != 'POST':
        return JsonResponse({
            'code': 405,
            'message': 'Method not allowed'
        }, status=405)
    
    user = _user_from_request(request)
    if not user:
        return JsonResponse({
            'code': 401,
            'message': '未登录'
        }, status=401)
    
    try:
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        errors = {}
        
        if not old_password:
            errors['old_password'] = '旧密码不能为空'
        elif not user.check_password(old_password):
            errors['old_password'] = '旧密码错误'
        
        if not new_password:
            errors['new_password'] = '新密码不能为空'
        elif len(new_password) < 6:
            errors['new_password'] = '新密码长度至少6位'
        
        if new_password != confirm_password:
            errors['confirm_password'] = '两次密码不一致'
        
        if errors:
            return JsonResponse({
                'code': 400,
                'message': '修改失败',
                'data': errors
            }, status=400)
        
        # 更新密码
        user.set_password(new_password)
        user.save()
        
        # 更新会话
        update_session_auth_hash(request, user)
        
        return JsonResponse({
            'code': 200,
            'message': '密码修改成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'code': 400,
            'message': str(e)
        }, status=400)

@csrf_exempt
def upload_avatar(request):
    """上传头像"""
    if request.method != 'POST':
        return JsonResponse({
            'code': 405,
            'message': 'Method not allowed'
        }, status=405)
    
    user = _user_from_request(request)
    if not user:
        return JsonResponse({
            'code': 401,
            'message': '未登录'
        }, status=401)
    
    try:
        if 'avatar' in request.FILES:
            # 处理文件上传
            avatar = request.FILES['avatar']
            
            # 删除旧头像
            if user.avatar:
                if os.path.exists(user.avatar.path):
                    os.remove(user.avatar.path)
            
            # 保存新头像
            user.avatar = avatar
            user.save()
            
            return JsonResponse({
                'code': 200,
                'message': '头像上传成功',
                'data': {
                    'avatar': user.avatar.url
                }
            })
        else:
            return JsonResponse({
                'code': 400,
                'message': '请选择文件'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'code': 400,
            'message': str(e)
        }, status=400)

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
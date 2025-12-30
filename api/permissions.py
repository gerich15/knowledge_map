from rest_framework import permissions
from django.shortcuts import get_object_or_404
from branches.models import Branch
from posts.models import Post


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет только владельцам объекта редактировать его.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD или OPTIONS запросы
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешаем запись только владельцу
        return obj.user == request.user


class IsPublicOrOwner(permissions.BasePermission):
    """
    Разрешение, которое проверяет, является ли объект публичным
    или пользователь является его владельцем.
    """
    def has_object_permission(self, request, view, obj):
        # Всегда разрешаем владельцу
        if obj.user == request.user:
            return True
        
        # Для постов проверяем черновик и приватность ветки
        if hasattr(obj, 'is_draft'):
            if obj.is_draft:
                return False
        
        # Для веток проверяем приватность
        if hasattr(obj, 'is_private'):
            if obj.is_private:
                return False
        
        # Для других объектов разрешаем безопасные методы
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class CanViewBranch(permissions.BasePermission):
    """
    Разрешение на просмотр ветки.
    """
    def has_permission(self, request, view):
        # Для создания всегда разрешаем аутентифицированным
        if request.method == 'POST':
            return request.user.is_authenticated
        
        return True
    
    def has_object_permission(self, request, view, obj):
        return obj.can_view(request.user)


class CanViewPost(permissions.BasePermission):
    """
    Разрешение на просмотр поста.
    """
    def has_object_permission(self, request, view, obj):
        return obj.can_view(request.user)
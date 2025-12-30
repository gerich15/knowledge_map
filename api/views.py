from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import datetime

from .serializers import (
    UserSerializer, BranchSerializer, PostSerializer,
    SubscriptionSerializer, LikeSerializer, TimelineSerializer
)
from .permissions import IsOwnerOrReadOnly, IsPublicOrOwner
from .pagination import StandardResultsSetPagination
from users.models import User
from branches.models import Branch
from posts.models import Post
from subscriptions.models import Subscription
from likes.models import Like


UserModel = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей"""
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'username'
    
    def get_permissions(self):
        """Разные permissions для разных действий"""
        if self.action in ['create', 'list']:
            permission_classes = [AllowAny]
        elif self.action in ['retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Оптимизация запросов"""
        queryset = super().get_queryset()
        return queryset.select_related().prefetch_related(
            'branches', 'posts'
        )
    
    @action(detail=True, methods=['get'])
    def timeline_data(self, request, username=None):
        """Получение данных временной шкалы пользователя"""
        user = get_object_or_404(UserModel, username=username)
        
        # Проверяем права доступа
        if user != request.user and not user.profile.is_public:
            return Response(
                {'error': 'Профиль пользователя приватный'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Получаем посты пользователя
        posts = Post.objects.filter(
            user=user,
            is_draft=False,
            branch__is_private=False
        ).select_related('branch').order_by('event_date')
        
        # Группируем по годам и месяцам
        timeline_data = {}
        for post in posts:
            year = post.event_date.year
            month = post.event_date.month
            
            if year not in timeline_data:
                timeline_data[year] = {}
            
            if month not in timeline_data[year]:
                timeline_data[year][month] = {
                    'posts_count': 0,
                    'branches': {}
                }
            
            timeline_data[year][month]['posts_count'] += 1
            
            branch_title = post.branch.title
            if branch_title not in timeline_data[year][month]['branches']:
                timeline_data[year][month]['branches'][branch_title] = 0
            timeline_data[year][month]['branches'][branch_title] += 1
        
        # Преобразуем в список для сериализации
        result = []
        for year, months in timeline_data.items():
            for month, data in months.items():
                result.append({
                    'year': year,
                    'month': month,
                    'posts_count': data['posts_count'],
                    'branches': data['branches']
                })
        
        serializer = TimelineSerializer(result, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def branches(self, request, username=None):
        """Получение веток пользователя"""
        user = get_object_or_404(UserModel, username=username)
        
        # Проверяем права доступа
        if user != request.user:
            branches = user.branches.filter(is_private=False)
        else:
            branches = user.branches.all()
        
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)


class BranchViewSet(viewsets.ModelViewSet):
    """ViewSet для веток"""
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'is_private', 'color']
    
    def get_queryset(self):
        """Оптимизация запросов и фильтрация по правам"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_authenticated:
            # Показываем публичные ветки и свои приватные
            queryset = queryset.filter(
                Q(is_private=False) | Q(user=user)
            )
        else:
            queryset = queryset.filter(is_private=False)
        
        return queryset.select_related('user', 'parent_branch').prefetch_related('posts')
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Получение постов ветки"""
        branch = self.get_object()
        
        # Проверяем права доступа
        if branch.is_private and branch.user != request.user:
            return Response(
                {'error': 'Ветка приватная'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        posts = branch.posts.filter(is_draft=False).order_by('-event_date')
        page = self.paginate_queryset(posts)
        
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для постов"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsPublicOrOwner]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'branch', 'post_type', 'is_draft']
    
    def get_queryset(self):
        """Оптимизация запросов и фильтрация по правам"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_authenticated:
            # Показываем публичные посты и свои черновики
            queryset = queryset.filter(
                Q(is_draft=False, branch__is_private=False) | 
                Q(user=user)
            )
        else:
            queryset = queryset.filter(
                is_draft=False,
                branch__is_private=False
            )
        
        return queryset.select_related('user', 'branch').prefetch_related('likes')
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Постановка/снятие лайка"""
        post = self.get_object()
        user = request.user
        
        like = Like.objects.filter(user=user, post=post).first()
        
        if like:
            like.delete()
            liked = False
        else:
            Like.objects.create(user=user, post=post)
            liked = True
        
        return Response({
            'liked': liked,
            'likes_count': post.likes_count
        })


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet для подписок"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Оптимизация запросов"""
        queryset = super().get_queryset()
        return queryset.select_related(
            'subscriber', 'target_user', 'target_branch__user'
        )
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем подписчика"""
        serializer.save(subscriber=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_subscriptions(self, request):
        """Получение подписок текущего пользователя"""
        subscriptions = self.get_queryset().filter(subscriber=request.user)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)


class LikeViewSet(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """ViewSet для лайков (только создание, удаление и список)"""
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Оптимизация запросов"""
        queryset = super().get_queryset()
        return queryset.select_related('user', 'post')
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя"""
        serializer.save(user=self.request.user)


class TimelineView(APIView):
    """API для получения данных временной шкалы"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, username):
        """Получение данных временной шкалы пользователя"""
        user = get_object_or_404(UserModel, username=username)
        
        # Проверяем права доступа
        if user != request.user:
            posts = Post.objects.filter(
                user=user,
                is_draft=False,
                branch__is_private=False
            )
        else:
            posts = Post.objects.filter(user=user)
        
        # Группировка по годам и месяцам
        timeline_data = {}
        
        for post in posts.select_related('branch'):
            year = post.event_date.year
            month = post.event_date.month
            
            key = f"{year}-{month:02d}"
            
            if key not in timeline_data:
                timeline_data[key] = {
                    'year': year,
                    'month': month,
                    'posts': [],
                    'branches': set()
                }
            
            timeline_data[key]['posts'].append({
                'id': post.id,
                'title': post.title,
                'branch': post.branch.title,
                'branch_color': post.branch.color,
                'event_date': post.event_date,
                'likes_count': post.likes_count
            })
            
            timeline_data[key]['branches'].add(post.branch.title)
        
        # Преобразуем в список и сортируем
        result = []
        for key, data in sorted(timeline_data.items(), reverse=True):
            data['posts_count'] = len(data['posts'])
            data['branches'] = list(data['branches'])
            data['posts'] = sorted(
                data['posts'],
                key=lambda x: x['event_date'],
                reverse=True
            )
            result.append(data)
        
        return Response(result)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import User
from branches.models import Branch
from posts.models import Post
from subscriptions.models import Subscription
from likes.models import Like


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    branches_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'avatar', 'website', 'location', 'birth_date',
            'is_verified', 'date_joined',
            'followers_count', 'following_count', 
            'branches_count', 'posts_count'
        ]
        read_only_fields = ['date_joined', 'is_verified']
        extra_kwargs = {
            'email': {'required': False},
            'password': {'write_only': True, 'required': False}
        }
    
    def create(self, validated_data):
        """Создание пользователя с хешированием пароля"""
        password = validated_data.pop('password', None)
        user = UserModel(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Обновление пользователя с обработкой пароля"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class BranchSerializer(serializers.ModelSerializer):
    """Сериализатор для ветки"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user'
    )
    parent_branch_title = serializers.CharField(
        source='parent_branch.title',
        read_only=True
    )
    
    class Meta:
        model = Branch
        fields = [
            'id', 'user', 'user_id', 'parent_branch', 'parent_branch_title',
            'title', 'color', 'description', 'is_private',
            'created_at', 'updated_at', 'posts_count', 'subscribers_count'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 
            'posts_count', 'subscribers_count'
        ]
    
    def validate(self, data):
        """Валидация данных ветки"""
        user = self.context['request'].user
        parent_branch = data.get('parent_branch')
        
        if parent_branch and parent_branch.user != user:
            raise serializers.ValidationError({
                'parent_branch': 'Можно использовать только свои ветки как родительские'
            })
        
        return data


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для поста"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user'
    )
    branch_title = serializers.CharField(
        source='branch.title',
        read_only=True
    )
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'user_id', 'branch', 'branch_title',
            'title', 'content', 'event_date', 'post_type',
            'is_draft', 'created_at', 'updated_at',
            'likes_count', 'comments_count'
        ]
        read_only_fields = [
            'created_at', 'updated_at',
            'likes_count', 'comments_count'
        ]
    
    def validate_event_date(self, value):
        """Валидация даты события"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                'Дата события не может быть в будущем'
            )
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""
    subscriber = UserSerializer(read_only=True)
    target_user = UserSerializer(read_only=True)
    target_branch = BranchSerializer(read_only=True)
    
    subscriber_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='subscriber'
    )
    target_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        source='target_user'
    )
    target_branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        source='target_branch'
    )
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'subscriber', 'subscriber_id',
            'target_user', 'target_user_id',
            'target_branch', 'target_branch_id',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Валидация данных подписки"""
        request = self.context.get('request')
        
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError('Требуется аутентификация')
        
        # Устанавливаем подписчика как текущего пользователя
        if 'subscriber' not in data:
            data['subscriber'] = request.user
        
        return data


class LikeSerializer(serializers.ModelSerializer):
    """Сериализатор для лайка"""
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user'
    )
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        write_only=True,
        source='post'
    )
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'user_id', 'post', 'post_id', 'created_at']
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Валидация данных лайка"""
        request = self.context.get('request')
        
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError('Требуется аутентификация')
        
        # Устанавливаем пользователя как текущего пользователя
        if 'user' not in data:
            data['user'] = request.user
        
        return data


class TimelineSerializer(serializers.Serializer):
    """Сериализатор для данных временной шкалы"""
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    posts_count = serializers.IntegerField()
    branches = serializers.DictField(
        child=serializers.IntegerField()
    )
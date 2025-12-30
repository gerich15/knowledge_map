from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone


class Post(models.Model):
    """
    Пост - основной контент, привязанный к дате на временной шкале.
    """
    class PostType(models.TextChoices):
        TEXT = 'text', _('Текст')
        LINK = 'link', _('Ссылка')
        IMAGE = 'image', _('Изображение')
        VIDEO = 'video', _('Видео')
        CODE = 'code', _('Код')
        ACHIEVEMENT = 'achievement', _('Достижение')
        MILESTONE = 'milestone', _('Веха')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('пользователь')
    )
    
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('ветка'),
        help_text=_('Ветка, к которой относится пост')
    )
    
    title = models.CharField(
        _('заголовок'),
        max_length=200,
        help_text=_('Краткий заголовок поста')
    )
    
    content = models.TextField(
        _('содержание'),
        help_text=_('Основное содержание поста')
    )
    
    event_date = models.DateField(
        _('дата события'),
        default=timezone.now,
        help_text=_('Дата, к которой привязан пост на временной шкале')
    )
    
    post_type = models.CharField(
        _('тип поста'),
        max_length=20,
        choices=PostType.choices,
        default=PostType.TEXT,
        help_text=_('Тип контента поста')
    )
    
    is_draft = models.BooleanField(
        _('черновик'),
        default=False,
        help_text=_('Скрыть пост от других пользователей')
    )
    
    created_at = models.DateTimeField(
        _('дата создания'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('дата обновления'),
        auto_now=True
    )
    
    likes_count = models.PositiveIntegerField(
        _('количество лайков'),
        default=0,
        editable=False
    )
    
    comments_count = models.PositiveIntegerField(
        _('количество комментариев'),
        default=0,
        editable=False
    )
    
    class Meta:
        verbose_name = _('пост')
        verbose_name_plural = _('посты')
        ordering = ['-event_date', '-created_at']
        indexes = [
            models.Index(fields=['event_date']),
            models.Index(fields=['user', 'event_date']),
            models.Index(fields=['branch', 'event_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('posts:detail', kwargs={'pk': self.pk})
    
    def update_counts(self):
        """Обновление счетчиков поста"""
        from likes.models import Like
        
        self.likes_count = Like.objects.filter(
            post=self
        ).count()
        
        # Здесь можно добавить счетчик комментариев, если будет модель Comment
        
        self.save(update_fields=['likes_count'])
    
    def can_view(self, user):
        """
        Проверка прав на просмотр поста.
        """
        if self.is_draft:
            if user.is_authenticated:
                return user == self.user or user.is_staff
            return False
        
        return self.branch.can_view(user)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Branch(models.Model):
    """
    Ветка - тематическая линия знаний пользователя.
    """
    class BranchColor(models.TextChoices):
        BLUE = 'blue', _('Синий')
        GREEN = 'green', _('Зеленый')
        RED = 'red', _('Красный')
        YELLOW = 'yellow', _('Желтый')
        PURPLE = 'purple', _('Фиолетовый')
        PINK = 'pink', _('Розовый')
        INDIGO = 'indigo', _('Индиго')
        GRAY = 'gray', _('Серый')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='branches',
        verbose_name=_('пользователь')
    )
    
    parent_branch = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='child_branches',
        blank=True,
        null=True,
        verbose_name=_('родительская ветка'),
        help_text=_('Можно создать под-ветку')
    )
    
    title = models.CharField(
        _('название'),
        max_length=200,
        help_text=_('Краткое название ветки')
    )
    
    color = models.CharField(
        _('цвет'),
        max_length=20,
        choices=BranchColor.choices,
        default=BranchColor.BLUE,
        help_text=_('Цвет для отображения на временной шкале')
    )
    
    description = models.TextField(
        _('описание'),
        max_length=1000,
        blank=True,
        null=True,
        help_text=_('Подробное описание темы ветки')
    )
    
    is_private = models.BooleanField(
        _('приватная'),
        default=False,
        help_text=_('Скрыть ветку от других пользователей')
    )
    
    created_at = models.DateTimeField(
        _('дата создания'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('дата обновления'),
        auto_now=True
    )
    
    posts_count = models.PositiveIntegerField(
        _('количество постов'),
        default=0,
        editable=False
    )
    
    subscribers_count = models.PositiveIntegerField(
        _('количество подписчиков'),
        default=0,
        editable=False
    )
    
    class Meta:
        verbose_name = _('ветка')
        verbose_name_plural = _('ветки')
        ordering = ['-created_at']
        unique_together = ['user', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('branches:detail', kwargs={'pk': self.pk})
    
    def update_counts(self):
        """Обновление счетчиков ветки"""
        from posts.models import Post
        from subscriptions.models import Subscription
        
        self.posts_count = Post.objects.filter(
            branch=self
        ).count()
        
        self.subscribers_count = Subscription.objects.filter(
            target_branch=self
        ).count()
        
        self.save(update_fields=['posts_count', 'subscribers_count'])
    
    def can_view(self, user):
        """
        Проверка прав на просмотр ветки.
        """
        if not self.is_private:
            return True
        
        if user.is_authenticated:
            return user == self.user or user.is_staff
        
        return False
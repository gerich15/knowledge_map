from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Like(models.Model):
    """
    Лайк (отметка "нравится") для поста.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('пользователь')
    )
    
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('пост')
    )
    
    created_at = models.DateTimeField(
        _('дата создания'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('лайк')
        verbose_name_plural = _('лайки')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_like'
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} ❤ {self.post.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновляем счетчик лайков у поста
        self.post.update_counts()
    
    def delete(self, *args, **kwargs):
        post = self.post
        super().delete(*args, **kwargs)
        # Обновляем счетчик лайков у поста
        post.update_counts()
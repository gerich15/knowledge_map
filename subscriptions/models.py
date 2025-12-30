from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError


class Subscription(models.Model):
    """
    Подписка пользователя на другого пользователя или конкретную ветку.
    """
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('подписчик')
    )
    
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_subscriptions',
        blank=True,
        null=True,
        verbose_name=_('целевой пользователь'),
        help_text=_('Подписка на все ветки пользователя')
    )
    
    target_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='branch_subscriptions',
        blank=True,
        null=True,
        verbose_name=_('целевая ветка'),
        help_text=_('Подписка только на конкретную ветку')
    )
    
    created_at = models.DateTimeField(
        _('дата создания'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('подписка')
        verbose_name_plural = _('подписки')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'target_user'],
                name='unique_user_subscription',
                condition=models.Q(target_branch__isnull=True)
            ),
            models.UniqueConstraint(
                fields=['subscriber', 'target_branch'],
                name='unique_branch_subscription'
            ),
            models.CheckConstraint(
                check=models.Q(target_user__isnull=False) | models.Q(target_branch__isnull=False),
                name='at_least_one_target'
            ),
        ]
    
    def __str__(self):
        if self.target_branch:
            return f"{self.subscriber} → {self.target_branch}"
        return f"{self.subscriber} → {self.target_user}"
    
    def clean(self):
        """
        Валидация модели подписки.
        """
        if self.target_user and self.target_branch:
            raise ValidationError(
                _('Подписка может быть только на пользователя ИЛИ на ветку')
            )
        
        if not self.target_user and not self.target_branch:
            raise ValidationError(
                _('Должен быть указан целевой пользователь или ветка')
            )
        
        if self.target_user and self.target_user == self.subscriber:
            raise ValidationError(
                _('Нельзя подписаться на самого себя')
            )
        
        if self.target_branch and self.target_branch.user == self.subscriber:
            raise ValidationError(
                _('Нельзя подписаться на свою собственную ветку')
            )
        
        if self.target_branch and self.target_branch.is_private:
            raise ValidationError(
                _('Нельзя подписаться на приватную ветку')
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # Обновляем счетчики
        if self.target_user:
            self.target_user.update_counts()
        elif self.target_branch:
            self.target_branch.user.update_counts()
            self.target_branch.update_counts()
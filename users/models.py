from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Расширенная модель пользователя для Knowledge Map.
    """
    bio = models.TextField(
        _('биография'),
        max_length=500,
        blank=True,
        null=True,
        help_text=_('Расскажите о себе')
    )
    
    avatar = models.ImageField(
        _('аватар'),
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('Загрузите ваш аватар')
    )
    
    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username

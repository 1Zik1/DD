from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Teacher
from datetime import date

@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):
    """
    Создает профиль педагога при регистрации нового пользователя
    
    ВАЖНО: Устанавливаем минимально допустимые значения для обязательных полей,
    чтобы избежать ошибки IntegrityError с NOT NULL
    """
    if created:
        Teacher.objects.create(
            user=instance,
            last_name="",  
            first_name="",  
            birth_date=date(1900, 1, 1)  
        )
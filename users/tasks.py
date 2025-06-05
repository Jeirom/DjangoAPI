from datetime import datetime

from django.utils import timezone
from celery import shared_task
from config.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from users.models import User
from school.models import Subscription


@shared_task
def sendmail_course_updated(course):
    """Отправляет уведомление о том, что курс обновлен"""
    subscription_course = Subscription.objects.filter(course=course)
    for subscription in subscription_course:
        print(f'Отправляем уведомление на почту {subscription.user.email}')
        send_mail(
            subject='Обновление курса',
            message=f'Курс {subscription.course.name}, на который вы подписаны, обновился!',
            from_email=EMAIL_HOST_USER,
            recipient_list=[subscription.user.email],
            fail_silently=False,
        )


@shared_task
def check_user_last_login():
    """Блокирует пользователя, если тот не авторизовался в течение 30 дней"""
    today = timezone.now().today().date()
    users = User.objects.filter(
        is_active=True,
        is_staff=False,
        is_superuser=False,
        last_login__isnull=False)
    for user in users:
        if user.last_login < today - datetime.timedelta(days=30):
            user.is_active = False
            user.save()
            print(f"Статус пользователя {user.email} изменен")
from django.db import models
from users.models import User
from typing import Literal


class Course(models.Model):
    """
    Модель, представляющая курс.

    Attributes:
        name (str): Название курса.
        preview (ImageField): Изображение, представляющее курс.
        description (str): Описание курса.
    """
    name: str = models.CharField(max_length=30, verbose_name='Курс')
    preview: models.ImageField = models.ImageField()
    description: str = models.TextField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Владелец')

class Lesson(models.Model):
    """
    Модель, представляющая урок в рамках курса.

    Attributes:
        name (str): Название урока.
        description (str): Описание урока.
        preview (ImageField): Изображение, представляющее урок.
        video (str): Ссылка на видео урока.
        course (Course): Курс, к которому принадлежит урок.
    """
    name: str = models.CharField(max_length=100, verbose_name='Урок')
    description: str = models.TextField(verbose_name='Описание урока')
    preview: models.ImageField = models.ImageField(blank=True, null=True)
    video: str = models.TextField(verbose_name='Ссылка на видео')
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Урок из курса", related_name='course')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Владелец')


class Payment(models.Model):
    """
    Модель, представляющая платеж за курс или урок.

    Attributes:
        user (User): Пользователь, осуществивший платеж.
        payment_date (datetime): Дата и время платежа.
        paid_course (Course): Курс, за который был совершен платеж.
        paid_lesson (Lesson): Урок, за который был совершен платеж.
        amount (decimal.Decimal): Сумма платежа.
        payment_method (Literal['cash', 'transfer']): Метод платежа.
    """
    PAYMENT_METHODS: list[tuple[str, str]] = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_date: models.DateTimeField = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    paid_course: Course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    paid_lesson: Lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='payments')
    amount: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method: Literal['cash', 'transfer'] = models.CharField(max_length=10, choices=PAYMENT_METHODS)

    def __str__(self) -> str:
        return f"Payment by {self.user} for {self.paid_course} on {self.payment_date.strftime('%Y-%m-%d')}"
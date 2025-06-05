from django.core.management.base import BaseCommand
from school.models import Lesson, Course
from users.models import User

class Command(BaseCommand):
    help = 'Добавляет данные в таблицу MyModel'

    def handle(self, *args, **kwargs):
        # Пример добавления одного объекта
        my_instance = Lesson(user=User.objects.get(email='test@gmail.com'), paid_course=Course.objects.get(name='Курс разработчика Python'), paid_lesson='Куплен весь курс по разработке в Python',

                             amount=17000, payment_method=('cash'))
        my_instance.save()
        self.stdout.write(self.style.SUCCESS('Данные успешно добавлены!'))


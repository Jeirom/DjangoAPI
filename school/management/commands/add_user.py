from django.core.management.base import BaseCommand
from school.models import Lesson, Course  # Импортируйте вашу модель

class Command(BaseCommand):
    help = 'Добавляет данные в таблицу MyModel'

    def handle(self, *args, **kwargs):
        # Пример добавления одного объекта
        my_instance = Lesson(user=User.objects.get(), description='В этом уроке вы будете точно заполнять данные '
                                                                        'таблицы с помощью кастомных команд. '
                                                                        'Ну или фикстурой', video='Not found',
                             course=Course.objects.get(name='Курс разработчика Python'))
        my_instance.save()
        self.stdout.write(self.style.SUCCESS('Данные успешно добавлены!'))

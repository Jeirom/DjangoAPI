from django.core.management.base import BaseCommand
from school.models import Course  # Импортируйте вашу модель

class Command(BaseCommand):
    help = 'Добавляет данные в таблицу MyModel'

    def handle(self, *args, **kwargs):
        # Пример добавления одного объекта
        my_instance = Course(name='Курс разработчика Python', description='Возможность попасть на стажировку в компаниях-партнёрах после курса! · '
                                                                          'Учитесь где удобно. Доступ навсегда. '
                                                                          'Сертификат NotSertificatus. Много практики · 0+')
        my_instance.save()
        self.stdout.write(self.style.SUCCESS('Данные успешно добавлены!'))

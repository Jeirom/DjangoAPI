from users.models import User


from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Course, Lesson, Subscription
from django.contrib.auth import get_user_model
from school.serializer import LessonSerializer
class CourseViewSetTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.moderator = User.objects.create_user(username='moderator', password='testpass', is_staff=True)
        self.course_data = {
            'name': 'Test Course',
            'preview': 'path/to/image.jpg',  # В реальности нужно использовать файловый объект
            'description': 'This is a test course description.'
        }

    def test_create_course_as_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('course-list'), self.course_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.get().name, 'Test Course')

    def test_create_course_as_moderator(self):
        self.client.login(username='moderator', password='testpass')
        response = self.client.post(reverse('course-list'), self.course_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_course(self):
        course = Course.objects.create(**self.course_data, owner=self.user)
        url = reverse('course-detail', kwargs={'pk': course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], course.name)

    def test_update_course_as_owner(self):
        course = Course.objects.create(**self.course_data, owner=self.user)
        self.client.login(username='testuser', password='testpass')
        updated_data = {
            'name': 'Updated Course',
            'preview': 'path/to/image.jpg',
            'description': 'Updated description.'
        }
        url = reverse('course-detail', kwargs={'pk': course.pk})
        response = self.client.put(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.name, 'Updated Course')

    def test_update_course_as_moderator(self):
        course = Course.objects.create(**self.course_data, owner=self.user)
        self.client.login(username='moderator', password='testpass')
        updated_data = {
            'name': 'Another Updated Course',
            'preview': 'path/to/image.jpg',
            'description': 'Another updated description.'
        }
        url = reverse('course-detail', kwargs={'pk': course.pk})
        response = self.client.put(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_as_owner(self):
        course = Course.objects.create(**self.course_data, owner=self.user)
        self.client.login(username='testuser', password='testpass')
        url = reverse('course-detail', kwargs={'pk': course.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)

    def test_delete_course_as_moderator(self):
        course = Course.objects.create(**self.course_data, owner=self.user)
        self.client.login(username='moderator', password='testpass')
        url = reverse('course-detail', kwargs={'pk': course.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_check_on_create(self):
        # Проверяем, что unauthed пользователь не может создавать курс
        response = self.client.post(reverse('course-list'), self.course_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


User = get_user_model()


class LessonCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        # Создаем курс и пользователя для тестов
        self.course = Course.objects.create(name='Test Course')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('lesson-create')  # Измените на правильный URL для вашей API

    def test_create_lesson_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'name': 'Test Lesson',
            'description': 'This is a test lesson',
            'preview': None,  # Замените на фактические данные об изображении, если необходимо
            'video': 'http://example.com/video',
            'course': self.course.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(Lesson.objects.get().name, 'Test Lesson')
        self.assertEqual(Lesson.objects.get().owner, self.user)

    def test_create_lesson_unauthenticated_user(self):
        data = {
            'name': 'Test Lesson',
            'description': 'This is a test lesson',
            'preview': None,
            'video': 'http://example.com/video',
            'course': self.course.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_with_forbidden_words(self):
        self.client.login(username='testuser', password='testpass')

        # Предположим, validate_forbidden_words не допускает слово 'forbidden'
        data = {
            'name': 'This contains forbidden',
            'description': 'This is a test lesson',
            'preview': None,
            'video': 'http://example.com/video',
            'course': self.course.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)  # Предполагаем, что валидация вызывает ошибку для поля 'name'

    def test_permissions_on_lesson_creation(self):
        # Проверяем разные ролики: модератор и обычный пользователь

        # Создание модератора
        moderator_user = User.objects.create_user(username='moderator', password='testpass', is_staff=True)
        self.client.login(username='moderator', password='testpass')

        data = {
            'name': 'Moderated Lesson',
            'description': 'This is a test lesson for moderators',
            'preview': None,
            'video': 'http://example.com/video',
            'course': self.course.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # проверка, что модератор не может создавать

        # Обычный пользователь
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SubscriptionAPIViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.course = Course.objects.create(name='Test Course')  # Замените на ваши поля
        self.client.force_authenticate(user=self.user)
        self.url = reverse('subscription')  # Здесь укажите URL для вашего SubscriptionAPIView

    def test_subscribe_to_course(self):
        response = self.client.post(self.url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Вы подписались')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        response = self.client.post(self.url, {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Вы отписались')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_to_non_existent_course(self):
        response = self.client.post(self.url, {'course': 9999})  # Не существующий ID курса
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LessonAPITestCase(APITestCase):

    def setUp(self):
        # Создаем пользователя и курс для тестирования
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(name='Test Course')

        # Создаем урок
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Test Description',
            video='http://testvideo.com',
            course=self.course,
            owner=self.user
        )

    def test_lesson_list(self):
        # Тестирование списка уроков
        url = reverse('lesson-list')  # Убедитесь, что имя URL соответствует вашему router или path
        response = self.client.get(url)
        lessons = Lesson.objects.all()
        serializer = LessonSerializer(lessons, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_lesson_retrieve(self):
        # Тестирование получения одного урока
        url = reverse('lesson-detail', args=[self.lesson.id])  # Замените на правильное имя URL
        response = self.client.get(url)
        serializer = LessonSerializer(self.lesson)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_lesson_update(self):
        # Тестирование обновления урока
        self.client.login(username='testuser', password='password')
        url = reverse('lesson-detail', args=[self.lesson.id])  # Замените на правильное имя URL
        data = {
            'name': 'Updated Lesson',
            'description': 'Updated Description',
            'video': 'http://updatedvideo.com',
            'course': self.course.id
        }
        response = self.client.put(url, data)
        self.lesson.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.lesson.name, 'Updated Lesson')
        self.assertEqual(self.lesson.description, 'Updated Description')

    def test_lesson_destroy(self):
        # Тестирование удаления урока
        self.client.login(username='testuser', password='password')
        url = reverse('lesson-detail', args=[self.lesson.id])  # Замените на правильное имя URL
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

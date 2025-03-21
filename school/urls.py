from school.apps import SchoolConfig
from django.urls import path
from rest_framework.routers import SimpleRouter
from school.views import (CourseViewSet, LessonListAPIView, LessonCreateAPIView,
                          LessonDestroyAPIView, LessonRetrieveAPIView, LessonUpdateAPIView, PaymentViewSet)


app_name = SchoolConfig.name

router = SimpleRouter()
router.register('', CourseViewSet)
# router.register('payment/', PaymentViewSet)


urlpatterns = [
    path('lesson/create/', LessonCreateAPIView.as_view(), name='create'),
    path('lesson/', LessonListAPIView.as_view(), name='list'),
    path('lesson/<int:pk>/delete', LessonDestroyAPIView.as_view(), name='delete'),
    path('lesson/<int:pk>/update', LessonUpdateAPIView.as_view(), name='update'),
    path('lesson/<int:pk>/', LessonRetrieveAPIView.as_view(), name='detail'),

]
urlpatterns += router.urls
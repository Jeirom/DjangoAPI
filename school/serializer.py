from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from school.models import Course, Lesson, Payment, Subscription


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseDetailSerializer(ModelSerializer):

    count_lesson_in_course = SerializerMethodField()
    lessons = LessonSerializer(read_only=True, many=True)

    def get_count_lesson_in_course(self, course):
        return course.lessons.count()

    class Meta:
        model = Course
        fields = ('name', 'count_lesson_in_course', 'lessons', 'preview', 'description')


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
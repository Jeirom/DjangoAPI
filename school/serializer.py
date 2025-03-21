from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from school.models import Course, Lesson, Payment


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
    preview = LessonSerializer()
    payment = PaymentSerializer()


    def get_count_lesson_in_course(self, lesson):
        return Lesson.objects.filter(course=lesson.course).count()

    class Meta:
        model = Course
        fields = ('name', 'preview', 'count_lesson_in_course', 'payment')



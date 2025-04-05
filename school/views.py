from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from school.models import Course, Lesson, Payment, Subscription
from school.serializer import CourseSerializer, LessonSerializer, CourseDetailSerializer, PaymentSerializer, \
    SubscriptionSerializer
from rest_framework import filters

from school.validators import validate_forbidden_words
from users.permissions import IsModer, IsOwner
from users.services import create_stripe_session, create_stripe_price, create_stripe_product


class CourseViewSet(ModelViewSet):

    queryset = Course.objects.all()
    permission_classes = [~IsModer, AllowAny,] # IsAuthenticated
    validators = [validate_forbidden_words]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (~IsModer,)
        elif self.action in ['update', 'retrieve']:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == 'destroy':
            self.permission_classes = (IsOwner | ~IsModer,)
        return super().get_permissions()


class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    validators = [validate_forbidden_words]

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (~IsModer,)
        elif self.action in ['update', 'retrieve']:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == 'destroy':
            self.permission_classes = (IsOwner | ~IsModer,)
        return super().get_permissions()


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ('course',)
    ordering_fields = ['payment_method', 'course', 'lesson', 'payment_date']


class LessonRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsModer | IsOwner,]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsModer | IsOwner, ]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner | IsModer]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['payment_method', 'course', 'lesson', 'payment_date']


class SubscriptionAPIView(APIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')
        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)
        if subs_item.exists():
            subs_item.delete()
            message = 'Вы отписались'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Вы подписались'
        return Response({"message": message})


class SubscriptionListAPIView(ListAPIView):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()


class PaymentCreateAPIView(CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, ~IsModer]

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     if not request.user.is_authenticated:
    #         return Response(
    #             {"error": "Authentication credentials were not provided."},
    #             status=status.HTTP_401_UNAUTHORIZED
    #         )
    #
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        payment = serializer.save()
        payment.user = self.request.user
        stripe_product_id = create_stripe_product(payment)
        payment.amount = payment.payment_sum
        price = create_stripe_price(
            stripe_product_id=stripe_product_id, amount=payment.amount
        )
        session_id, payment_link = create_stripe_session(price=price)
        payment.session_id = session_id
        payment.payment_url = payment_link
        payment.save()


class PaymentRetrieveAPIView(RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ("course_paid", "lesson_paid", "payment_method")
    ordering_fields = ("date_of_payment",)


class PaymentUpdateAPIView(UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentDestroyAPIView(DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
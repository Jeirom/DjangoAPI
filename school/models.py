from django.db import models


# Create your models here.
class Course(models.Model):

    name = models.CharField(max_length=30, verbose_name='Курс')
    preview = models.ImageField()
    description = models.TextField(max_length=100)


class Lesson(models.Model):

    name = models.CharField()
    description = models.TextField()
    preview = models.ImageField()
    video = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Урок из курса")


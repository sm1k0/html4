from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):  # переделываем стандартный класс User
    is_moderator = models.BooleanField(default=False)  # для дальнейшей реализации системы жалоб

def user_directory_path(instance,filename):
    return 'users/user_{0}/{1}'.format(instance.user.id, 'logo'+filename[filename.find('.'):])

class Profile(models.Model):
    user = models.OneToOneField(to=get_user_model(), on_delete=models.CASCADE)
    bio = models.CharField(max_length=100)
    logo_image = models.ImageField(upload_to=user_directory_path, null=True)


class Voting(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=300)
    type = models.SmallIntegerField()  # вид голосования 1 - radiobutton 2 - checkbox
    options = models.TextField()  # json массив вариантов ответа
    user = models.ForeignKey(to=get_user_model(), on_delete=models.SET_NULL, null=True)


class Comment(models.Model):
    text = models.CharField(max_length=100)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.SET_NULL, null=True)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE)


class Vote(models.Model):  # при многовыборочном голосовании создаётся несколько штук
    option = models.SmallIntegerField()  # индекс ответа в json массиве
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE)

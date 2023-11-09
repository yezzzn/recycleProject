from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


User.add_to_class(
    "phone", models.CharField(max_length=15, default="")
)  # django 에서 제공하는 User모델에 원하는 필드를 더하기 위한 코드
User.add_to_class("person", models.BooleanField(default=False))
User.add_to_class("datetime", models.DateTimeField(auto_now_add=True))
User.add_to_class("pointuser", models.IntegerField(default=100))


# Create your models here.
class Category(models.Model):  # DB에 Category라는 필드 생성
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Item(models.Model):# DB에 item 필드 생성
    category = models.ForeignKey(
        Category, related_name="items", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    point = models.IntegerField()
    image = models.ImageField(upload_to="item_images", blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name="items", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Database(models.Model): # 재활용품 데이터를 받는 Database라는 필드 생성 
    kind = models.CharField(max_length=30)
    num = models.IntegerField()
    image = models.ImageField(max_length=100)
    confidence = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Apartdb(models.Model):
    citizen = models.CharField(max_length=30, default="")
    apartment = models.CharField(max_length=30, default="")
    dong = models.CharField(max_length=30, default="")
    ho = models.CharField(max_length=30, default="")


class Aparterror(models.Model): # 아파트 불량률을 따로 저장하기 위한 필드
    apartment = models.CharField(max_length=30, default="")
    error = models.FloatField(default=0)


class PointDB(models.Model): # 아파트 포인트를 저장하기 위한 필드 
    user = models.CharField(max_length=30, default="")
    pointuser = models.IntegerField(default=100)

    def __str__(self):
        return self.name


class Apartdatabase(models.Model): # 아파트 정보 입력시 정보를 저장하기 위한 테이블 
    citizen = models.CharField(max_length=30, default="")
    apartment = models.CharField(max_length=30, default="")
    dong = models.CharField(max_length=30, default="")
    ho = models.CharField(max_length=30, default="")
    pay = models.IntegerField(default=30000)
    badcitizen = models.BooleanField(default=False)

    def __str__(self):
        return self.apartment


class Image(models.Model): # 마일리지 페이지의 상품을 저장하기 위한 필드 
    product = models.TextField(default="")
    price = models.IntegerField(default=100)
    image = models.ImageField(upload_to="item_images")


class Video(models.Model): # 실시간 영상을 위해 이미지 경로를 저장하기 위한 필드 
    image = models.ImageField(max_length=100)


class logtable(models.Model): # 유저가 입장한 시간을 저장하기 위한 필드 
    user_id = models.CharField(max_length=30, default="")
    datetime = models.DateTimeField(auto_now_add=True)

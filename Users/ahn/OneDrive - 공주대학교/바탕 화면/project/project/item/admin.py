from django.contrib import admin

# Register your models here.
from .models import (
    Category,
    Item,
    Image,
)  # item/models.py에 존재하는 모델 Category, Item, Image를 포함함

admin.site.register(Category)  # admin 사이트에 Category라는 모델을 가입시킴
admin.site.register(Item)
admin.site.register(Image)

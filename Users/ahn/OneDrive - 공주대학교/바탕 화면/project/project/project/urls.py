from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core.views import index  # core 폴더의 views.py 폴더 내부의 index함수를 가져옴
from core.views import contact  # core 폴더의 views.py 폴더 내부의 contact함수를 가져옴

urlpatterns = [
    path(
        "contact/", contact, name="contact"
    ),  # contact/라는 url 실행시 core.views.py 내부의 contact라는 함수 호출 별명을 "contact"로 붙임
    path(
        "items/", include("item.urls")
    ),  # item/ url에 추가적으로 item폴더의 urls.py path를 포함 시킴
    path("", include("core.urls")),  # 기본 url에 core 폴더의 urls.py path를 포함시킴
    path("admin/", admin.site.urls),  # admin/ url 호출시 django에서 제공하는 DB 사이트 url로 이동
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # media 경로를 settings.py 에 존재하는 MEDIA_URL로 정의

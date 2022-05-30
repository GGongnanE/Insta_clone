from django.contrib import admin
from .models import Profile, Follow


# 팔로우 내용을 표 양식으로 볼 때 사용
class FollowInline(admin.TabularInline):
    model = Follow
    fk_name = 'from_user'


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'nickname', 'user']
    list_display_links = ['nickname', 'user']
    search_fields = ['nickname']  # 정보 검색


@admin.register(Follow)
class FollowAdin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'created_at']
    list_display_links = ['from_user', 'to_user', 'created_at']

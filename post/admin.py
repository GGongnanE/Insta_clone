from django import forms
from django.contrib import admin
from .models import Post



# Register your models here.
class PostForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Post
        fields = '__all__'


'''
    - admin.register 데코레이터를 이용한다. 
    1. admin 페이지에서 id, author, nickname, content, created_at을 리스트에 보이게 하고, 
       author, nickname, content에만 링크가 걸리도록 설정한다. 
    2. nickname은 사용자가 포스트를 작성할 때 따로 입력하지 않기 때문에, nickname을 가져오는 함수를 만든다. 
'''
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'nickname', 'content', 'created_at']
    list_display_links = ['author', 'nickname', 'content']

    def nickname(request, post):
        return post.author.profile.nickname


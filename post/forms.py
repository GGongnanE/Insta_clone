from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    photo = forms.ImageField(label='')
    content = forms.CharField(label='', widget=forms.Textarea(attrs={
        'class' : 'post-new-content',
        'rows' : 5,
        'cols' : 50,
        'placeholder' : '140자 까지 등록가능합니다.'
    }))

    class Meta:
        model = Post
        fields = ['photo', 'content']


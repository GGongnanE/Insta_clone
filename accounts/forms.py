from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    username = forms.CharField(label='사용자명', widget=forms.TextInput(attrs={
        'pattern': '[a-zA-Z0-9]+',
        'title': '특수문자, 공백 입력불가',
    }))

    nickname = forms.CharField(label='닉네임')
    picture = forms.ImageField(label='프로필 사진', required=False)

    # Meta class (Django) -> 정렬, DB 테이블 이름 등의 모델 단위 옵션 설정
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)


    '''
        유효성 검사
        - clean_nickname : 닉네임 검증 
        - clean_email : 이메일 검증 
    '''
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')

        if Profile.objects.filter(nickname = nickname).exists():
            raise forms.ValidationError('이미 존재하는 닉네임입니다.')
        return nickname

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError('이미 사용중인 이메일입니다.')
        return email

    # 프로필 사진이 없으면 None으로 처리
    def clean_picture(self):
        picture = self.cleaned_data.get('picture')

        if not picture:
            picture = None
        return picture

    # user 정보 저장
    def save(self):
        user = super().save()
        Profile.objects.create(
            user = user,
            nickname = self.cleaned_data['nickname'],
            picture=self.cleaned_data['picture'],
        )
        return user
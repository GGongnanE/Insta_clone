from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


def user_path(instance, filename):
    from random import choice
    import string

    # 대소문자 관계 없이 8번 반복하여 문자를 불러온다.
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]

    return 'accounts/{}/{}.{}'.format(instance.user.username, pid, extension)


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField('별명', max_length=20, unique=True)

    # 사진 처리
    picture = ProcessedImageField(upload_to=user_path,
                                  processors=[ResizeToFill(150, 150)],
                                  format='JPEG',
                                  options={'quality': 100},
                                  blank=True
                                 )

    about = models.CharField(max_length=300, blank=True)
    GENDER_CHOICE = (
        ('선택안함', '선택안함'),
        ('남성', '남성'),
        ('여성', '여성')
    )
    gender = models.CharField('성별(선택사항)', max_length=10, choices=GENDER_CHOICE, default='N')

    def __str__(self):
        return self.nickname
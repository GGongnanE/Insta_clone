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
    follow_set = models.ManyToManyField('self',  # 자신을 참조
                                        blank=True,  # 아무도 팔로우 안한 상태
                                        through='Follow',  # 중간 모델
                                        symmetrical=False)  # 비대칭 관계

    def __str__(self):
        return self.nickname

    # 해당 유저를 팔로우하고 있는 유저
    @property
    def get_follower(self):
        return [i.from_user for i in self.follower_user.all()]

    # 해당 유저가 팔로우하고 있는 유저
    @property
    def get_following(self):
        return [i.to_user for i in self.follow_user.all()]

    @property
    def follower_count(self):
        return len(self.get_follower)

    @property
    def following_count(self):
        return len(self.get_following)

    def is_follower(self, user):
        return user in self.get_follower

    def is_following(self, user):
        return user in self.get_following


# Follow 모델
class Follow(models.Model):
    # Follow user
    from_user = models.ForeignKey(Profile,
                                  related_name='follow_user',
                                  on_delete=models.CASCADE)
    # Follower
    to_user = models.ForeignKey(Profile,
                                related_name='follower_user',
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # 관계가 언제 생겼는지 작성

    # 인스턴스 추적 양식 지정
    def __str__(self):
        return '{} -> {}'.format(self.from_user, self.to_user)

    class Meta:
        unique_together = (
            ('from_user', 'to_user')
        )

from django.db import models
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


def photo_path(instance, filename):
    from time import strftime
    from random import choice
    import string

    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return '{}/{}/{}.{}'.format(strftime('post/%y/%m/%d/'), instance.author.username, pid, extension)


# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = ProcessedImageField(upload_to=photo_path,
                                processors=[ResizeToFill(600,600)],
                                format='PNG',
                                options={ 'quality':100 })
    content = models.CharField(max_length=200, help_text="최대 200자 입력 가능")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.content


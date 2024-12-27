from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수 항목입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    


# Create your models here.
class User(AbstractUser):
    email = models.EmailField('이메일', unique=True)
    username = models.CharField('닉네임', max_length=100)
    profile_image = models.ImageField('프로필 이미지', upload_to='profile_images/', null=True, blank=True)

    followings = models.ManyToManyField(
        'self',  # 자기 자신과의 관계
        symmetrical=False,  # 대칭 관계가 아님 (단방향)
        related_name='followers',  # 역참조 이름
        through='Follow',  # 중간 테이블
        blank= True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name='followed_users', on_delete=models.CASCADE)  # 팔로우를 하는 사용자
    following = models.ForeignKey(
        User, related_name='following_users', on_delete=models.CASCADE)  # 팔로우받는 사용자
    created_at = models.DateTimeField(auto_now_add=True)  # 팔로우한 시간

    class Meta:
        unique_together = ('follower', 'following')  # 중복 팔로우 방지




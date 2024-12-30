from django.db import models
from django.conf import settings

class Product(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    title = models.CharField('제목', max_length=200)
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    view_count = models.PositiveIntegerField('조회수', default=0)
    product_image = models.ImageField(
        upload_to='product_images/',
        default='product_images/default.jpg'
    )

    def __str__(self):
        return self.title

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_comments')

    def __str__(self):
        return f'{self.author} - {self.content}'


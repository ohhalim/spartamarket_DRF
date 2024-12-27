from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.ArticleListCreate.as_view(), name='article_list_create'),
    path('<int:article_pk>/', views.ArticleDetail.as_view(), name='article_detail'),
    path('<int:article_pk>/comments/', views.CommentListCreate.as_view(), name='comments'),
    path('<int:article_pk>/comments/<int:comment_pk>/like/', views.CommentLike.as_view(), name='comment_like'),
    path('<int:article_pk>/delete/', views.ArticleDetail.as_view(), name='article_delete'),
    path('<int:article_pk>/update/', views.ArticleDetail.as_view(), name='article_update'),

]
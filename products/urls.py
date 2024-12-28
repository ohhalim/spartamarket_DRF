from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListCreate.as_view(), name='product_list_create'),
    path('<int:product_pk>/', views.ProductDetail.as_view(), name='product_detail'),
    path('<int:product_pk>/comments/', views.CommentListCreate.as_view(), name='comments'),
    path('<int:product_pk>/comments/<int:comment_pk>/like/', views.CommentLike.as_view(), name='comment_like'),
    path('<int:product_pk>/delete/', views.ProductDetail.as_view(), name='product_delete'),
    path('<int:product_pk>/update/', views.ProductDetail.as_view(), name='product_update'),
]
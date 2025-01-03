from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.Signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),  # 회원정보 조회 및 수정
    path('<str:username>/', views.user_profile, name='user_profile'),    
    path('<int:user_pk>/follow/', views.follow, name='follow'), #팔로우/언팔로우 토
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('subs/', views.subs, name='subs'),
    path('upload/', views.upload, name='upload'),
    path('video/<int:pk>/', views.watch, name='watch'),
    path('stream/<int:pk>/', views.stream, name='stream'),
    path('video/<int:pk>/like/', views.like, name='like'),
    path('video/<int:pk>/comment/', views.comment, name='comment'),
    path('video/<int:pk>/delete/', views.delete_video, name='delete_video'),
    path('channel/<str:username>/', views.channel, name='channel'),
    path('channel/<int:pk>/subscribe/', views.subscribe, name='subscribe'),
]
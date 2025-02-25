from django.urls import path
from . import views

urlpatterns = [
    path('',views.user,name='user'),
    path('recommend/',views.recommend,name='recommend'),
    path('detail/',views.detail,name='detail')
]
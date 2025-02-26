from django.urls import path
from . import views

urlpatterns = [
    path('',views.user,name='user'),
    path('recommend/',views.recommend,name='recommend'),
    path('detail/',views.detail,name='detail'),
    path('request_current_menu_API/',views.request_current_menu_API,name='request_current_menu_API'),
    path('request_recommendation_API/',views.request_recommendation_API,name='request_recommendation_API'),
]
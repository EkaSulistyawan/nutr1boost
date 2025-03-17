from django.urls import path
from . import views

urlpatterns = [
    path('',views.user,name='user'),
    path('recommend/',views.recommend,name='recommend'),
    path('detail/',views.detail,name='detail'),
    path('api/request_current_menu/',views.request_current_menu_API,name='request_current_menu_API'),
    path('api/request_recommendation/',views.request_recommendation_API,name='request_recommendation_API'),
    path('api/detect_and_set_current_menu/',views.detect_current_menu_API,name='detect_current_menu_API'),
    path('api/reset_current_menu/',views.reset_current_menu_API,name='reset_current_menu_API'),
    path('api/get_new_recommendation/',views.get_new_recommendation_API,name='get_new_recommendation_API'),
    path('officer/change_menu/',views.change_menu,name='change_menu'),
    path('officer/register_current_menu/',views.register_current_menu,name='register_current_menu')
]
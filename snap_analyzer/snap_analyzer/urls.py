from django.contrib import admin
from django.urls import path

from snap_analyzer_django import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.orders_app, name='home'),
    path('parser/', views.parser),
    path('upload/', views.upload, name='upload'),
    path('<int:blog_id>/', views.detail, name='detail'),
    path('drive/<int:blog_id_drive>/', views.drive_detail, name='drive_detail'),
    path('node/<int:blog_id_node>/', views.node_detail, name='node_detail'),
]

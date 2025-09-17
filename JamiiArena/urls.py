from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='landing'),
    path('auth/', include('accounts.urls')),
    path('arena/', include('core.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
]

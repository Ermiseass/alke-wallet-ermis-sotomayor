from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
urlpatterns = [path('admin/', admin.site.urls), path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(http_method_names=['post', 'options']), name='logout'), path('', include('gestion.urls'))]

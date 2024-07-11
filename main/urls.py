from django.urls import path
from .views import index, other_page, BBLoginView, profile
from django.contrib.auth.views import LogoutView

app_name = 'main'
urlpatterns = [
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/profile/', profile, name='profile'),

]

from django.urls import path
from .views import index, other_page, BBLoginView, ChangeUserInfoView, profile, BBPasswordChangeView, RegisterUserView, \
    RegisterDoneView, user_activate, DeleteUserView, by_rubric, detail, profile_bb_detail
from django.contrib.auth.views import LogoutView

app_name = 'main'
urlpatterns = [
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/password/change', BBPasswordChangeView.as_view(), name='password_change'),
    path('<int:rubric_pk>/<int:pk>', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/<int:pk>', profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/', profile, name='profile'),

]

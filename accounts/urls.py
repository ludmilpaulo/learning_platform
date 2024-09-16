from django.urls import path
from .views import PasswordResetView, PasswordResetConfirmView, UserProfileView, UserSignupView, UserLoginView, get_user_profile, update_user_profile

urlpatterns = [
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('account/user/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('account/profile/<int:user_id>/', get_user_profile, name='get-user-profile'),
    path('account/update/<int:user_id>/', update_user_profile, name='update-user-profile'),

]
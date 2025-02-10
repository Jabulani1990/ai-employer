from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView,UserProfileView, SkillListView, AssignSkillsView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user_register"),
    path("login/", LoginView.as_view(), name="login"),
     path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("skills/", SkillListView.as_view(), name="skill_list"),
    path("assign-skills/", AssignSkillsView.as_view(), name="assign-skills"),
]
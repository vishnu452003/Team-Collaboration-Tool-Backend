from django.urls import path, include
from .views import RegisterView, LoginView,PasswordResetRequestView, PasswordResetConfirmView
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet)
router.register(r'projects', ProjectViewSet)

urlpatterns = [
     path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
     path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

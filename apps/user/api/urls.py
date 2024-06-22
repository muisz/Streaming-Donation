from rest_framework.routers import DefaultRouter
from apps.user.api import views

urlpatterns = []

router = DefaultRouter()
router.register('', views.auth_view, basename='auth')

urlpatterns += router.urls


from rest_framework.routers import DefaultRouter
from apps.user.api import views

urlpatterns = []

router = DefaultRouter()
router.register('', views.AuthView, basename='auth')

urlpatterns += router.urls


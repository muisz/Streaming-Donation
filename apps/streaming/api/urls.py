from rest_framework.routers import DefaultRouter

from apps.streaming.api import views


urlpatterns = []

router = DefaultRouter()
router.register('streams', views.streaming_view, basename='streams')

urlpatterns += router.urls

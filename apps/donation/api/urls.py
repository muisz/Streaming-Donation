from rest_framework.routers import DefaultRouter

from apps.donation.api import views


urlpatterns = []

router = DefaultRouter()
router.register('donations', views.donation_view, basename='donation')
router.register('midtrans/callback', views.midtrans_callback_view, basename='midtrans-callback')

urlpatterns += router.urls

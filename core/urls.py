from django.urls import path
from . import views

urlpatterns = [
    path("NFTs/", views.nft_marketplace, name="nft"),
    path("governance/", views.governance, name="governance"),
    path("voting/", views.voting, name="voting"),
    path('collection/<str:nft_type>/', views.collection_detail, name='collection_detail'),
    path('api/check-nft-availability/<str:nft_type>/<int:serial_number>/', views.check_nft_availability, name='check_nft_availability'),
]

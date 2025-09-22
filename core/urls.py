from django.urls import path
from . import views

urlpatterns = [
    path("NFTs/", views.nft_marketplace, name="nft"),
    path("governance/", views.governance, name="governance"),
    path("voting/", views.voting, name="voting"),
    path('collection/<str:nft_type>/', views.collection_detail, name='collection_detail'),
    #path('api/check-nft-availability/<str:nft_type>/<int:serial_number>/', views.check_nft_availability, name='check_nft_availability'),
    path('api/payments/add/', views.add_funds, name='add-funds'),
    path('buy-ticket/<str:nft_tier>/<int:competition_id>/', views.buy_ticket, name='buy_ticket'),
]

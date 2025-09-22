from django.contrib import admin

from .models import NFT, NFTCollection, Competition, Contestant

admin.site.register(NFT)
admin.site.register(NFTCollection)
admin.site.register(Competition)
admin.site.register(Contestant)
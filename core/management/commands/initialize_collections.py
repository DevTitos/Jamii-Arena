from django.core.management.base import BaseCommand
from core.models import NFTCollection, NFT

class Command(BaseCommand):
    help = 'Initialize NFT collections with max supply and create sample NFTs'

    def handle(self, *args, **options):
        # Create collections with max supply
        collections_data = [
            {'nft_type': 'vNFT', 'name': 'Voting Power NFT', 'max_supply': 10000},
            {'nft_type': 'aNFT', 'name': 'Artist NFT', 'max_supply': 10000},
            {'nft_type': 'pNFT', 'name': 'Patron NFT', 'max_supply': 100},
            {'nft_type': 'VVIP', 'name': 'VVIP Ticket', 'max_supply': 2000},
            {'nft_type': 'VIP', 'name': 'VIP Ticket', 'max_supply': 3000},
            {'nft_type': 'REG', 'name': 'Regular Ticket', 'max_supply': 5000},
        ]
        
        for data in collections_data:
            collection, created = NFTCollection.objects.get_or_create(
                nft_type=data['nft_type'],
                defaults={'name': data['name'], 'max_supply': data['max_supply']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {collection}'))
            else:
                self.stdout.write(self.style.WARNING(f'{collection} already exists'))

        # Create sample NFTs
        collections = NFTCollection.objects.all()
        for collection in collections:
            # Create first 5 NFTs for each collection as examples
            for i in range(1, 6):
                nft, created = NFT.objects.get_or_create(
                    collection=collection,
                    serial_number=i,
                    defaults={'price': collection.get_default_price(), 'is_available': True}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created {nft}'))

        self.stdout.write(self.style.SUCCESS('✅ All collections and sample NFTs initialized successfully!'))
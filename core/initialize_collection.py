def initialize_collections():
    """Create all NFT collections with their max supply"""
    collections_data = [
        {'nft_type': 'vNFT', 'name': 'Voting Power NFT', 'max_supply': 10000},
        {'nft_type': 'aNFT', 'name': 'Artist NFT', 'max_supply': 10000},
        {'nft_type': 'pNFT', 'name': 'Patron NFT', 'max_supply': 100},
        {'nft_type': 'VVIP', 'name': 'VVIP Ticket', 'max_supply': 2000},
        {'nft_type': 'VIP', 'name': 'VIP Ticket', 'max_supply': 3000},
        {'nft_type': 'REG', 'name': 'Regular Ticket', 'max_supply': 5000},
    ]
    
    for data in collections_data:
        NFTCollection.objects.get_or_create(
            nft_type=data['nft_type'],
            defaults={'name': data['name'], 'max_supply': data['max_supply']}
        )
    
    print("NFT collections initialized with max supply!")

def create_initial_nfts():
    """Create some initial NFTs for testing"""
    collections = NFTCollection.objects.all()
    
    for collection in collections:
        # Create first 10 NFTs for each collection
        for i in range(1, 11):
            NFT.objects.create(
                collection=collection,
                serial_number=i,
                price=collection.get_default_price(),
                is_available=True
            )
    
    print("Initial NFTs created!")
import json

def get_simple_metadata(nft_type, serial_number):
    """Returns metadata for any NFT type in one function"""
    
    base_data = {
        "name": "",
        "description": "",
        "image": "ipfs://YOUR_BASE_IMAGE_HASH",  # Use same image or customize per type
        "attributes": []
    }
    
    # Set properties based on NFT type
    if nft_type == 'vNFT':
        base_data["name"] = f"Voting Power NFT #{serial_number}"
        base_data["description"] = "This NFT gives you voting power in Ujamaa Canvas."
        base_data["attributes"] = [
            {"trait_type": "Purpose", "value": "Voting"},
            {"trait_type": "Voting Power", "value": "1"}
        ]
    
    elif nft_type == 'aNFT':
        base_data["name"] = f"Artist NFT #{serial_number}"
        base_data["description"] = "Official verified artist on Ujamaa Canvas."
        base_data["attributes"] = [
            {"trait_type": "Role", "value": "Artist"},
            {"trait_type": "Status", "value": "Verified"}
        ]
    
    elif nft_type == 'pNFT':
        base_data["name"] = f"Patron NFT #{serial_number}"
        base_data["description"] = "Special NFT for Ujamaa Canvas patrons."
        base_data["attributes"] = [
            {"trait_type": "Role", "value": "Patron"},
            {"trait_type": "Rarity", "value": "Rare"}
        ]
    
    elif nft_type == 'VVIP':
        base_data["name"] = f"VVIP Ticket #{serial_number}"
        base_data["description"] = "VVIP ticket with premium access."
        base_data["attributes"] = [
            {"trait_type": "Ticket Tier", "value": "VVIP"},
            {"trait_type": "Benefits", "value": "Best Seats + Meet & Greet"}
        ]
    
    elif nft_type == 'VIP':
        base_data["name"] = f"VIP Ticket #{serial_number}"
        base_data["description"] = "VIP ticket with priority access."
        base_data["attributes"] = [
            {"trait_type": "Ticket Tier", "value": "VIP"},
            {"trait_type": "Benefits", "value": "Priority Seating"}
        ]
    
    elif nft_type == 'REG':
        base_data["name"] = f"Regular Ticket #{serial_number}"
        base_data["description"] = "General admission ticket."
        base_data["attributes"] = [
            {"trait_type": "Ticket Tier", "value": "Regular"},
            {"trait_type": "Access", "value": "General Admission"}
        ]
    
    return base_data
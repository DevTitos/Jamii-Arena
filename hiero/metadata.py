artist_metadata = {
    "name": "Jamii Arena Artist Profile",
    "description": "Official verified artist profile on Jamii Arena.",
    "image": "ipfs://bafybeigexampleartistavatar",  # IPFS hash of profile image
    "external_url": "https://app.ujamaacanvas.com/artist/john-doe-123",
    "attributes": [
        {
            "trait_type": "Artist Name",
            "value": "John Doe"
        },
        {
            "trait_type": "Category",
            "value": "Music"
        },
        {
            "trait_type": "Verification Status",
            "value": "Verified"
        },
        {
            "trait_type": "Join Date",
            "value": "2025-01-15"
        },
        {
            "trait_type": "Platform",
            "value": "Jamii Arena"
        }
    ]
}

# Usage:
# artist_nft_id = mint_nft(client, "0.0.1234001", artist_metadata, operator_key)


ticket_metadata = {
    "name": "Jamii Arena: Afrobeat Night - VVIP Pass",
    "description": "NFT Ticket granting access and voting rights to the Afrobeat Night finale.",
    "image": "ipfs://bafybeigticketqrcodeimage",  # IPFS hash of ticket art/QR code
    "external_url": "https://app.ujamaacanvas.com/event/afrobeat-night-567",
    "attributes": [
        {
            "trait_type": "Event",
            "value": "Afrobeat Night Finals"
        },
        {
            "trait_type": "Date",
            "value": "2024-03-20T19:00:00Z"
        },
        {
            "trait_type": "Venue",
            "value": "Nairobi Cultural Center"
        },
        {
            "trait_type": "Seat Type",
            "value": "VVIP Pass"
        },
        {
            "trait_type": "Voting Power",
            "value": "3"
        },
        {
            "display_type": "date",
            "trait_type": "Door Opens",
            "value": 1710961200  # Unix timestamp
        }
    ]
}

# Usage:
# ticket_nft_id = mint_nft(client, "0.0.1234002", ticket_metadata, operator_key)

patron_metadata = {
    "name": "Jamii Arena Founding Patron",
    "description": "Awarded to early supporters and patrons of the Ujamaa Canvas platform.",
    "image": "ipfs://bafybeiexclusivebadgeart",  # IPFS hash of exclusive art
    "external_url": "https://app.ujamaacanvas.com/patron/badges",
    "attributes": [
        {
            "trait_type": "Tier",
            "value": "Founding Patron"
        },
        {
            "trait_type": "Rarity",
            "value": "Rare"
        },
        {
            "trait_type": "Year",
            "value": "2025"
        },
        {
            "trait_type": "Platform",
            "value": "Jamii Arena"
        }
    ]
}

# Usage:
# patron_nft_id = mint_nft(client, "0.0.1234004", patron_metadata, operator_key)

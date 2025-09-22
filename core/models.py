from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

class Competition(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('registration_open', 'Registration Open'),
        ('voting_open', 'Voting Open'),
        ('finished', 'Finished'),
    ]
    
    CATEGORY_CHOICES = [
        ('music', 'Music'),
        ('dance', 'Dance'),
        ('comedy', 'Comedy'),
        ('poetry', 'Poetry'),
        ('Martial Arts', 'Martial Arts'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    venue = models.CharField(max_length=200, default="Afrobeat Night")
    date_time = models.DateTimeField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    organizer = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_type': 'organizer'})
    prize_pool = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # In HTS (fiat-backed)
    registration_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0)  # In HTS (fiat-backed)
    created_date = models.DateTimeField(auto_now_add=True)

    def get_gradient(self):
        """Get gradient based on category"""
        gradients = {
            'music': 'from-[#00f0d6] to-[#007a6c]',
            'dance': 'from-[#9d4edd] to-[#5a189a]',
            'comedy': 'from-[#ff6b6b] to-[#c0392b]',
            'poetry': 'from-[#4cc9f0] to-[#4895ef]',
            'Martial Arts': 'from-[#f9c74f] to-[#f9844a]',  # Note: Space in choice
        }
        return gradients.get(self.category, 'from-[#4cc9f0] to-[#4895ef]')
    
    def get_icon(self):
        """Get icon based on category"""
        icons = {
            'music': 'fa-microphone-alt',
            'dance': 'fa-music',
            'comedy': 'fa-theater-masks',
            'poetry': 'fa-feather-alt',
            'Martial Arts': 'fa-fist-raised',  # Note: Space in choice
        }
        return icons.get(self.category, 'fa-ticket-alt')
    
    def get_tickets_sold(self):
        """Get number of tickets sold across all NFT collections for this competition"""
        total_sold = 0
        for collection in self.nftcollection_set.all():
            total_sold += collection.nfts.filter(is_available=False).count()
        return total_sold
    
    def get_max_tickets(self):
        """Get maximum tickets available across all NFT collections"""
        total_max = 0
        for collection in self.nftcollection_set.all():
            total_max += collection.max_supply
        return total_max
    
    def is_sold_out(self):
        """Check if all tickets are sold"""
        return self.get_tickets_sold() >= self.get_max_tickets()
    
    def get_ticket_price(self):
        """Get base ticket price - you might want to customize this per competition"""
        # This could be based on the registration fee or a separate field
        return float(self.registration_fee) / 10  # Example conversion to HBAR
    
    @property
    def available_ticket_collections(self):
        """Get available NFT collections for this competition"""
        return self.nftcollection_set.filter(current_supply__lt=models.F('max_supply'))

    def __str__(self):
        return self.title

class Contestant(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    artist = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'user_type': 'artist'})
    performance_title = models.CharField(max_length=200)
    performance_video_ipfs_hash = models.CharField(max_length=100)  # Link to performance video
    is_approved = models.BooleanField(default=False)
    registered_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['competition', 'artist']

    def __str__(self):
        return f"{self.artist.user.username} - {self.performance_title}"

class Vote(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    voter_wallet = models.CharField(max_length=64)  # Must be an NFT ticket owner
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='votes_received')
    hcs_message_id = models.CharField(max_length=100)  # HCS consensus message ID
    voted_at = models.DateTimeField(auto_now_add=True)
    voting_power = models.IntegerField(default=1)  # 1 vote per NFT ticket

    class Meta:
        unique_together = ['competition', 'voter_wallet', 'contestant']  # 1 vote per artist per voter

    def __str__(self):
        return f"Vote for {self.contestant} by {self.voter_wallet}"

class RevenueDistribution(models.Model):
    DISTRIBUTION_TYPE = [
        ('prize', 'Prize to Winner'),
        ('organizer', 'Revenue to Organizer'),
        ('platform', 'Platform Fee'),
        ('artist_pool', 'Pool for Participating Artists'),
    ]
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    distribution_type = models.CharField(max_length=20, choices=DISTRIBUTION_TYPE)
    recipient_wallet = models.CharField(max_length=64)  # Wallet address of recipient
    transaction_hash = models.CharField(max_length=100)  # HTS Transaction Hash
    distributed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.distribution_type} - {self.amount} HTS for {self.competition.title}"
    

class NFTCollection(models.Model):
    """Master table for each NFT type and its max supply"""
    NFT_TYPES = [
        ('vNFT', 'Voting NFT'),
        ('aNFT', 'Artist NFT'), 
        ('pNFT', 'Patron NFT'),
        ('VVIP', 'VVIP Ticket'),
        ('VIP', 'VIP Ticket'),
        ('REG', 'Regular Ticket'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    nft_type = models.CharField(max_length=4, choices=NFT_TYPES, unique=True)
    name = models.CharField(max_length=100)
    max_supply = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100000)]
    )
    current_supply = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    nft_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "NFT Collection"
        verbose_name_plural = "NFT Collections"

    def __str__(self):
        return f"{self.get_nft_type_display()} ({self.current_supply}/{self.max_supply})"
    
    def is_sold_out(self):
        return self.current_supply >= self.max_supply
    
    def available_count(self):
        return self.max_supply - self.current_supply
    
    def get_properties(self):
        """Return properties based on NFT type"""
        properties = {
            'vNFT': {'title': 'Voting Power NFT', 'gradient': 'from-[#00f0d6] to-[#007a6c]', 'rarity': 'rare', 'votes': 5, 'price': 1000.0},
            'aNFT': {'title': 'Artist Profile NFT', 'gradient': 'from-[#ff6b6b] to-[#c0392b]', 'rarity': 'uncommon', 'votes': 3, 'price': 0.5},
            'pNFT': {'title': 'Founding Patron NFT', 'gradient': 'from-[#f9c74f] to-[#f9844a]', 'rarity': 'legendary', 'votes': 10, 'price': 5000.0},
            'VVIP': {'title': 'VVIP Access Pass', 'gradient': 'from-[#9d4edd] to-[#5a189a]', 'rarity': 'epic', 'votes': 3, 'price': 3000.0},
            'VIP': {'title': 'VIP Experience Ticket', 'gradient': 'from-[#4361ee] to-[#3a0ca3]', 'rarity': 'rare', 'votes': 2, 'price': 2000},
            'REG': {'title': 'General Admission', 'gradient': 'from-[#4cc9f0] to-[#4895ef]', 'rarity': 'common', 'votes': 1, 'price': 1000},
        }
        return properties.get(self.nft_type, {})
    
    def get_default_price(self):
        return self.get_properties().get('price', 1.0)
    
    def get_title(self):
        return self.get_properties().get('title', 'NFT')
    
    def get_gradient(self):
        return self.get_properties().get('gradient', 'from-[#4cc9f0] to-[#4895ef]')
    
    def get_rarity(self):
        return self.get_properties().get('rarity', 'common')
    
    def get_rarity_display(self):
        return self.get_properties().get('rarity', 'Common').title()
    
    def get_votes(self):
        return self.get_properties().get('votes', 1)
    
    def get_icon(self):
        icons = {
            'vNFT': 'fa-vote-yea', 'aNFT': 'fa-palette', 'pNFT': 'fa-crown',
            'VVIP': 'fa-gem', 'VIP': 'fa-star', 'REG': 'fa-ticket-alt'
        }
        return icons.get(self.nft_type, 'fa-certificate')

class NFT(models.Model):
    """Individual NFT instance"""
    collection = models.ForeignKey(NFTCollection, on_delete=models.CASCADE, related_name='nfts')
    serial_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    owner_wallet = models.CharField(max_length=64, blank=True)
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['collection', 'serial_number']
        ordering = ['collection', 'serial_number']

    def __str__(self):
        return f"{self.collection.get_nft_type_display()} #{self.serial_number}"
    
    def save(self, *args, **kwargs):
        # Prevent creating more NFTs than max supply
        if not self.pk:  # Only on creation
            if self.serial_number > self.collection.max_supply:
                raise ValueError(f"Serial number cannot exceed max supply of {self.collection.max_supply}")
            
            # Update collection supply count
            if self.serial_number > self.collection.current_supply:
                self.collection.current_supply = self.serial_number
                self.collection.save()
        
        super().save(*args, **kwargs)

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Extend AbstractUser for flexibility
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)

    # Role system (Artist, Audience, Judge, Sponsor, Admin)
    ROLE_CHOICES = [
        ('artist', 'Artist'),
        ('audience', 'Audience'),
        ('judge', 'Judge'),
        ('sponsor', 'Sponsor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='audience')

    # Hedera integration
    hedera_account_id = models.CharField(max_length=100, blank=True, null=True, help_text="Hedera account ID")
    did = models.CharField(max_length=200, blank=True, null=True, help_text="Decentralized Identifier")
    public_key = models.TextField(blank=True, null=True)
    private_key_encrypted = models.TextField(blank=True, null=True)

    # Profile Info
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Engagement / gamification
    reputation_points = models.IntegerField(default=0)  # Earned via votes, contributions, projects

    def __str__(self):
        return f"{self.username} ({self.role})"


# NFT Ticket ownership (links audience/judge to events)
class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="tickets")
    nft_token_id = models.CharField(max_length=100, unique=True, help_text="Hedera NFT Token ID")
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.nft_token_id} for {self.event}"


# Votes (NFT-backed votes from audience/judges)
class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    performance = models.ForeignKey("events.Performance", on_delete=models.CASCADE, related_name="votes")
    nft_vote_id = models.CharField(max_length=100, unique=True, help_text="NFT ID minted as a vote")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.voter} voted for {self.performance}"


# Sponsor contributions (FT-backed, using Hedera Stablecoin/Custom Token)
class Contribution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contributions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    token_transaction_id = models.CharField(max_length=150, help_text="Hedera Token Transfer Tx ID")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sponsor {self.sponsor} contributed {self.amount}"

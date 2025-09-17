from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid
import string
import random
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from cryptography.fernet import Fernet
import os
from cryptography.fernet import Fernet
import uuid
import base64
from dotenv import load_dotenv
load_dotenv()

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
    ('None', 'Prefer not to say')
)

USER_TYPE_CHOICES = [
        ('audience', 'Audience'),
        ('artist', 'Artist'),
        ('voter', 'Voter/Patron'),
        ('organizer', 'Organizer'),
    ]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(upload_to="profile", blank=True, null=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, default="None")
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="audience")
    funds = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def name(self) -> str:
        return self.user.get_full_name()
    

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    public_key = models.CharField(max_length=256, blank=True, null=True)
    private_key = models.CharField(max_length=256, blank=True, null=True, editable=False)
    recipient_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Encrypt private keys before saving."""
        if self.private_key:
            key_str = str(self.private_key)  # Ensure it's a string
            if not key_str.startswith("gAAAA"):  # Avoid double encryption
                self.private_key = self.encrypt_key(key_str)
        super().save(*args, **kwargs)

    def encrypt_key(self, key: str) -> str:
        """
        Encrypt the private key using Fernet.
        """
        try:
            secret_key = os.getenv('SECRET_KEY')
            if not secret_key:
                raise ValueError("Missing SECRET_KEY in environment variables")
            
            # Ensure the secret key is 32 bytes long
            key_bytes = secret_key.encode()
            key_base64 = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
            f = Fernet(key_base64)
            return f.encrypt(key.encode()).decode()
        except Exception as e:
            raise ValueError(f"Encryption error: {e}")

    def decrypt_key(self) -> str:
        """
        Decrypt the private key using Fernet.
        """
        try:
            secret_key = os.getenv('SECRET_KEY')
            if not secret_key:
                raise ValueError("Missing SECRET_KEY in environment variables")
            
            # Ensure the secret key is 32 bytes long
            key_bytes = secret_key.encode()
            key_base64 = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
            f = Fernet(key_base64)
            return f.decrypt(self.private_key.encode()).decode()
        except Exception as e:
            raise ValueError(f"Decryption error: {e}")

    def __str__(self):
        return f"{self.user.username} Wallet"
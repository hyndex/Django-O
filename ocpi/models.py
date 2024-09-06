from django.db import models
from django.contrib.auth.models import User

class OCPIParty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ocpi_party')
    party_id = models.CharField(max_length=3, unique=True)  # e.g., "CPO"
    country_code = models.CharField(max_length=2)  # ISO 3166-1 alpha-2 country code
    name = models.CharField(max_length=255)  # Name of the organization
    website = models.URLField(blank=True, null=True)  # Optional website for the organization
    ocpi_token = models.CharField(max_length=255, unique=True)  # Token used for OCPI authentication
    roles = models.CharField(max_length=10, choices=[('CPO', 'CPO'), ('eMSP', 'eMSP')])  # Role of the party
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.party_id} - {self.name}"

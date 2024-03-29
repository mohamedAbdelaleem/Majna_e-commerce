from django.db import models
from brands.models import Brand
from accounts.models import Distributor
from common.validators import validate_max_filename_length



BRAND_APPLICATION_CHOICES = [
    ("inprogress", "In Progress"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


class BrandApplication(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    authorization_doc = models.CharField(validators=[validate_max_filename_length])
    identity_doc = models.CharField(validators=[validate_max_filename_length])
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=BRAND_APPLICATION_CHOICES, default="inprogress"
    )

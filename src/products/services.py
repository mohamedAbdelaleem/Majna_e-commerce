from typing import List, Dict
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from brands.services import BrandSelector
from utils.storage import SupabaseStorageService
from utils.helpers import generate_dated_filepath
from common.validators import validate_file_format, validate_file_size
from stores import models as store_models
from . import models as product_models

MAX_ALBUM_ITEMS = 3


class ProductService:
    def __init__(self) -> None:
        self.supabase = SupabaseStorageService()
        self.brand_selector = BrandSelector()

    def create(self, product_data: Dict, distributor_pk) -> product_models.Product:
        print(product_data)
        is_authorized = self.brand_selector.has_distributor(
            product_data["brand_pk"], distributor_pk
        )
        if not is_authorized:
            raise PermissionDenied(
                "Distributor doesn't authorized for the selected brand"
            )
        self._validate_album_items(product_data["album"])
        self._validate_inventory(product_data["inventory"], distributor_pk)

        with transaction.atomic():
            product = product_models.Product.objects.create(
                title=product_data["title"],
                description=product_data["description"],
                price=product_data["price"],
                sub_category=product_data["sub_category"],
                brand_id=product_data["brand_pk"],
            )
            self.add_album_items(
                product_pk=product.pk, album_items_data=product_data["album"]
            )
            self.add_inventory(
                product_pk=product.pk, inventory_data=product_data["inventory"]
            )

        return product

    def add_album_items(self, product_pk, album_items_data: List[Dict]):
        for item in album_items_data:
            image, is_cover = item["image"], item["is_cover"]
            image_path = f"product_images/{generate_dated_filepath(image.name)}"
            with transaction.atomic():
                self.supabase.upload(
                    image,
                    "images",
                    image_path,
                    file_options={"content-type": "image/*"},
                )
                product_models.AlbumItem.objects.create(
                    product_id=product_pk, img_url=image_path, is_cover=is_cover
                )

    def add_inventory(self, product_pk, inventory_data: List[Dict]):
        for item in inventory_data:
            store_pk, quantity = item["store_pk"], item["quantity"]
            product_models.Inventory.objects.create(
                product_id=product_pk, store_id=store_pk, quantity=quantity
            )

    def _validate_album_items(self, album_items_data: List[Dict]):
        if len(album_items_data) > MAX_ALBUM_ITEMS:
            raise ValidationError("Album Items can not be more than 10")

        num_of_covers = 0
        for item in album_items_data:
            image, is_cover = item["image"], item["is_cover"]
            validate_file_size(image, settings.ALBUM_ITEM_MAX_SIZE)
            validate_file_format(image, ["jpg", "png", "jpeg"])
            if is_cover:
                num_of_covers += 1

        if num_of_covers != 1:
            raise ValidationError("Album must have One cover image")

    def _validate_inventory(self, inventory: List[Dict], distributor_pk):
        stores = [inv["store_pk"] for inv in inventory]
        stores_num = (
            store_models.Store.objects.filter(
                pk__in=stores, distributor_id=distributor_pk
            )
            .values("distributor_id")
            .count()
        )

        if stores_num != len(stores):
            raise ValidationError("Invalid stores provided")

from typing import List, Dict
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Subquery, Sum
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework.exceptions import PermissionDenied
from brands.services import BrandSelector
from carts.models import CartItem
from common.api.exceptions import Conflict
from utils.storage import SupabaseStorageService
from common.validators import validate_file_format
from addresses import models as addresses_models
from . import models as product_models


MAX_ALBUM_ITEMS = 3


class ProductService:
    def __init__(self) -> None:
        self.supabase = SupabaseStorageService()
        self.brand_selector = BrandSelector()
        self.album_service = AlbumService()

    def create(self, product_data: Dict, distributor_pk) -> product_models.Product:
        is_authorized = self.brand_selector.has_distributor(
            product_data["brand_pk"], distributor_pk
        )
        if not is_authorized:
            raise PermissionDenied(
                "Distributor doesn't authorized for the selected brand"
            )
        self.album_service._validate_album_items(product_data["album"])
        self._validate_inventory(product_data["inventory"], distributor_pk)

        with transaction.atomic():
            product = product_models.Product.objects.create(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                sub_category=product_data["sub_category"],
                brand_id=product_data["brand_pk"],
            )
            self.album_service.add_album_items(
                product_pk=product.pk, album_items_data=product_data["album"]
            )
            self.add_inventory(
                product_pk=product.pk, inventory_data=product_data["inventory"]
            )

        return product

    def update(self, product: product_models.Product, distributor_pk: int, **data):
        with transaction.atomic():
            if "inventory" in data:
                self._validate_inventory(data["inventory"], distributor_pk)
                product_models.Inventory.objects.filter(product_id=product.pk).delete()
                self.add_inventory(product.pk, data["inventory"])
                del data["inventory"]
            for key, val in data.items():
                product.__setattr__(key, val)
            product.full_clean()
            product.save()

    def delete(self, product: product_models.Product):
        with transaction.atomic():
            product_models.FavoriteItem.objects.filter(product_id=product.pk).delete()
            CartItem.objects.filter(product_id=product.pk).delete()
            product.is_active = False
            product.save()

    def add_inventory(self, product_pk, inventory_data: List[Dict]):
        for item in inventory_data:
            store_pk, quantity = item["store_pk"], item["quantity"]
            product_models.Inventory.objects.create(
                product_id=product_pk, store_id=store_pk, quantity=quantity
            )

    def _validate_inventory(self, inventory: List[Dict], distributor_pk):
        stores = [inv["store_pk"] for inv in inventory]
        if len(stores) == 0:
            raise ValidationError("No stores are provided!")

        stores_num = (
            addresses_models.Store.objects.filter(
                pk__in=stores, distributor_id=distributor_pk
            )
            .values("distributor_id")
            .count()
        )

        if stores_num != len(stores):
            raise ValidationError("Invalid stores provided")

    def bulk_add_to_favorite(self, product_ids: List[int], customer_pk: int):
        exist_items = product_models.FavoriteItem.objects.filter(
            product_id__in=product_ids
        ).values("product_id")
        exist_items = [r["product_id"] for r in exist_items]
        product_ids = set(product_ids).difference(set(exist_items))
        items = []
        for pk in product_ids:
            item = product_models.FavoriteItem(product_id=pk, customer_id=customer_pk)
            item.full_clean()
            items.append(item)
        product_models.FavoriteItem.objects.bulk_create(items)

    def add_to_favorite(self, product_id: int, customer_id: int):
        favorite_item = product_models.FavoriteItem(
            product_id=product_id, customer_id=customer_id
        )
        favorite_item.full_clean()
        favorite_item.save()

    def remove_from_favorite(self, favorite_item: product_models.FavoriteItem):
        favorite_item.delete()


class ProductSelector:
    def __init__(self):
        self.supabase = SupabaseStorageService()

    def product_list(self, search: str = None, ordering: List[str] = None, **filters):
        products = product_models.Product.objects.filter(**filters)
        if search:
            search_str = search.replace(" ", " | ")
            query = SearchQuery(search_str, search_type="raw")
            vector = SearchVector("name", "description", config="english")
            search_result = (
                product_models.Product.objects.annotate(search=vector)
                .filter(search=query)
                .values("id")
            )

            rank_vector = SearchVector("name", weight="A") + SearchVector(
                "description", weight="B"
            )
            rank = SearchRank(rank_vector, query, weights=[0.2, 0.4, 0.6, 0.8])
            products = (
                products.filter(id__in=search_result)
                .annotate(rank=rank)
                .filter(rank__gte=0.3)
                .order_by("-rank")
            )
            if ordering:
                products = products.order_by(*ordering, "-rank")

        elif ordering:
            products = products.order_by(*ordering)

        return products

    def category_product_list(self, category_pk: int, **filters):
        sub_categories = product_models.SubCategory.objects.filter(
            category_id=category_pk
        ).values("id")
        return self.product_list(
            sub_category_id__in=Subquery(sub_categories), **filters
        )

    def get_cover_image_url(self, product_pk):
        cover_image_item = product_models.AlbumItem.objects.get(
            product_id=product_pk, is_cover=True
        )
        return cover_image_item.image.url

    def get_image_url(self, path: str) -> str:
        duration = timedelta(days=2).total_seconds()
        url = self.supabase.get_url("images", path, duration)
        return url

    def favorite_item_list(self, **filters):
        items = product_models.FavoriteItem.objects.filter(**filters)
        return items

    def get_total_quantity(self, product_id: int):
        total_quantity = product_models.Inventory.objects.filter(
            product_id=product_id
        ).aggregate(total=Sum("quantity", default=0))["total"]
        return total_quantity

    def get_inventory(self, product_id: int):
        inventory = product_models.Inventory.objects.filter(
            product_id=product_id
        ).values("store_id", "quantity")
        return inventory

    def is_owner(self, distributor_pk: int, product_pk: int):
        products = self.product_list(
            id=product_pk, inventory__store__distributor_id=distributor_pk
        )
        return products.exists()

    def get_product(self, **criteria):
        return product_models.Product.objects.get(**criteria)

    def get_product_owner(self, product_id):
        store = product_models.Inventory.objects.filter(product_id=product_id)[0:1]
        return store.distributor


class AlbumService:
    def add_album_items(self, product_pk, album_items_data: List[Dict]):
        """Bulk add album items. This method used when creating a product"""
        album_items = []
        for item in album_items_data:
            image, is_cover = item["image"], item["is_cover"]
            album_item = product_models.AlbumItem(
                product_id=product_pk, image=image, is_cover=is_cover
            )
            album_item.full_clean()
            album_items.append(album_item)
        product_models.AlbumItem.objects.bulk_create(album_items)

    def add_album_item(self, product_pk, album_item_data: Dict):
        """Add album item to a product album"""
        album_items_count = product_models.AlbumItem.objects.filter(
            product_id=product_pk
        ).count()
        if album_items_count == MAX_ALBUM_ITEMS:
            raise Conflict(f"Max number of album items is {MAX_ALBUM_ITEMS}")

        image, is_cover = album_item_data["image"], album_item_data["is_cover"]
        validate_file_format(image, ["png", "jpg", "jpeg"])
        with transaction.atomic():
            album_item = product_models.AlbumItem(
                product_id=product_pk, image=image, is_cover=is_cover
            )
            if is_cover:
                product_models.AlbumItem.objects.filter(
                    product_id=product_pk, is_cover=True
                ).update(is_cover=False)
            album_item.full_clean()
            album_item.save()

    def update_album_item(self, album_item: product_models.AlbumItem, data: Dict):
        with transaction.atomic():
            if "is_cover" in data and data["is_cover"]:
                product_models.AlbumItem.objects.filter(
                    product_id=album_item.product_id, is_cover=True
                ).update(is_cover=False)
                album_item.is_cover = True
            if "image" in data:
                album_item.image = data["image"]
                validate_file_format(album_item.image, ["png", "jpg", "jpeg"])
            album_item.full_clean()
            album_item.save()

    def delete_album_item(self, album_item: product_models.AlbumItem):
        if album_item.is_cover:
            raise Conflict("Can't delete the cover image")
        album_item.delete()

    def _validate_album_items(self, album_items_data: List[Dict]):
        if len(album_items_data) > MAX_ALBUM_ITEMS:
            raise ValidationError("Album Items can not be more than 10")

        num_of_covers = 0
        for item in album_items_data:
            image, is_cover = item["image"], item["is_cover"]
            validate_file_format(image, ["jpg", "png", "jpeg"])
            if is_cover:
                num_of_covers += 1

        if num_of_covers != 1:
            raise ValidationError("Album must have One cover image")

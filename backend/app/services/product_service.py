from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from backend.app.models.product import Product
from backend.app.repositories.category_repository import CategoryRepository
from backend.app.schemas.category import CategoryResponse

from ..repositories.product_repository import ProductRepository
from ..schemas.product import ProductCreate, ProductListResponse, ProductResponse


class ProductService:
    def __init__(self, db: Session):
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    def get_all_products(self) -> ProductListResponse:
        products = self.product_repository.get_all()
        products_response = [ProductResponse.validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products))

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )
        return ProductResponse.model_validate(product)

    def get_product_by_category(self, category_id: int) -> ProductListResponse:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Category with {category_id} not found",
            )
        products = self.product_repository.get_by_category(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(
            products=products_response, total=len(products_response)
        )

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        category = self.category_repository.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Category with {product_data.category_id} does not exist",
            )
        product = self.product_repository.create(product_data)
        return ProductResponse.model_validate(product)


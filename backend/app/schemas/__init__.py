from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


class WechatLoginIn(BaseModel):
    code: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class DevLoginIn(BaseModel):
    openid: str = "dev_openid_001"
    nickname: str = "开发用户"
    avatar: str = ""


class AdminLoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    nickname: str
    avatar: str
    phone: str
    role: str
    status: str

    class Config:
        from_attributes = True


class UserUpdateIn(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None


class RegionOut(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    level: int
    code: str
    sort: int
    status: int

    class Config:
        from_attributes = True


class RegionCreateIn(BaseModel):
    parent_id: Optional[int] = None
    name: str
    level: int
    code: str = ""
    sort: int = 0
    status: int = 1


class CategoryOut(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    icon: str
    sort: int
    status: int
    children: List["CategoryOut"] = []

    class Config:
        from_attributes = True


class CategoryCreateIn(BaseModel):
    parent_id: Optional[int] = None
    name: str
    icon: str = ""
    sort: int = 0
    status: int = 1


class CategoryUpdateIn(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[int] = None
    parent_id: Optional[int] = None


class MerchantApplyIn(BaseModel):
    merchant_name: str
    merchant_type: str = "PERSONAL"
    phone: str
    wechat: str = ""
    description: str = ""
    province_id: Optional[int] = None
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    town_id: Optional[int] = None
    village_id: Optional[int] = None
    address: str = ""
    business_hours: str = ""
    materials: List[str] = []


class MerchantUpdateIn(BaseModel):
    merchant_name: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    town_id: Optional[int] = None
    village_id: Optional[int] = None
    address: Optional[str] = None
    business_hours: Optional[str] = None


class MerchantPublicOut(BaseModel):
    id: int
    merchant_name: str
    merchant_type: str
    avatar: str
    description: str
    phone: str
    province_id: Optional[int]
    city_id: Optional[int]
    district_id: Optional[int]
    town_id: Optional[int]
    village_id: Optional[int]
    address: str
    business_hours: str
    verify_status: str

    class Config:
        from_attributes = True


class MerchantPrivateOut(MerchantPublicOut):
    wechat: str
    reject_reason: str
    materials: str
    user_id: int


class ProductImageIn(BaseModel):
    image_url: str
    sort: int = 0


class ProductCreateIn(BaseModel):
    category_id: int
    name: str
    cover_image: str = ""
    description: str = ""
    specs: str = ""
    price: Optional[Decimal] = None
    price_unit: str = "DAY"
    price_unit_custom: str = ""
    deposit: Optional[Decimal] = None
    min_rent_days: int = 1
    stock: int = 1
    province_id: Optional[int] = None
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    town_id: Optional[int] = None
    village_id: Optional[int] = None
    address: str = ""
    images: List[ProductImageIn] = []
    submit: bool = False


class ProductUpdateIn(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    specs: Optional[str] = None
    price: Optional[Decimal] = None
    price_unit: Optional[str] = None
    price_unit_custom: Optional[str] = None
    deposit: Optional[Decimal] = None
    min_rent_days: Optional[int] = None
    stock: Optional[int] = None
    province_id: Optional[int] = None
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    town_id: Optional[int] = None
    village_id: Optional[int] = None
    address: Optional[str] = None
    images: Optional[List[ProductImageIn]] = None  # None=不改图片
    submit: bool = True


class ProductImageOut(BaseModel):
    id: int
    image_url: str
    sort: int

    class Config:
        from_attributes = True


class ProductListItem(BaseModel):
    id: int
    name: str
    cover_image: str
    price: Optional[Decimal]
    price_unit: str
    price_unit_custom: str
    deposit: Optional[Decimal]
    town_id: Optional[int]
    village_id: Optional[int]
    address: str
    view_count: int
    favorite_count: int
    merchant_id: int
    merchant_name: Optional[str] = None
    category_id: int
    audit_status: Optional[str] = None
    shelf_status: Optional[str] = None


class ProductDetailOut(BaseModel):
    id: int
    merchant_id: int
    category_id: int
    name: str
    cover_image: str
    description: str
    specs: str
    price: Optional[Decimal]
    price_unit: str
    price_unit_custom: str
    deposit: Optional[Decimal]
    min_rent_days: int
    stock: int
    province_id: Optional[int]
    city_id: Optional[int]
    district_id: Optional[int]
    town_id: Optional[int]
    village_id: Optional[int]
    address: str
    view_count: int
    favorite_count: int
    images: List[ProductImageOut] = []
    merchant: Optional[MerchantPublicOut] = None
    is_favorited: bool = False
    audit_status: Optional[str] = None
    shelf_status: Optional[str] = None
    reject_reason: Optional[str] = None


class FavoriteIn(BaseModel):
    target_type: str
    target_id: int


class BannerOut(BaseModel):
    id: int
    title: str
    image_url: str
    link_type: str
    link_value: str
    sort: int

    class Config:
        from_attributes = True


class BannerIn(BaseModel):
    title: str = ""
    image_url: str
    link_type: str = ""
    link_value: str = ""
    sort: int = 0
    status: int = 1


class AuditIn(BaseModel):
    action: str = Field(description="approve|reject")
    reason: str = ""


class PageResult(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    user_count: int
    merchant_count: int
    product_count: int
    pending_merchants: int
    pending_products: int
    view_count: int
    favorite_count: int
    inquiry_count: int

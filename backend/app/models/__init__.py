from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, Enum):
    USER = "USER"
    MERCHANT = "MERCHANT"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class MerchantVerifyStatus(str, Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class MerchantType(str, Enum):
    PERSONAL = "PERSONAL"
    ENTERPRISE = "ENTERPRISE"


class ProductAuditStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ProductShelfStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class PriceUnit(str, Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    TIME = "TIME"
    MONTH = "MONTH"
    NEGOTIABLE = "NEGOTIABLE"
    CUSTOM = "CUSTOM"


class FavoriteTargetType(str, Enum):
    PRODUCT = "PRODUCT"
    MERCHANT = "MERCHANT"


class InquiryType(str, Enum):
    PHONE = "PHONE"
    WECHAT = "WECHAT"
    NAV = "NAV"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    openid: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(64), default="寰俊鐢ㄦ埛")
    avatar: Mapped[str] = mapped_column(String(512), default="")
    phone: Mapped[str] = mapped_column(String(20), default="")
    role: Mapped[str] = mapped_column(String(20), default=UserRole.USER.value, index=True)
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE.value)

    merchant: Mapped[Optional["Merchant"]] = relationship(back_populates="user", uselist=False)


class AdminAccount(Base, TimestampMixin):
    __tablename__ = "admin_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Region(Base, TimestampMixin):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 1-5
    code: Mapped[str] = mapped_column(String(32), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    icon: Mapped[str] = mapped_column(String(512), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)


class Merchant(Base, TimestampMixin):
    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    merchant_name: Mapped[str] = mapped_column(String(128), nullable=False)
    merchant_type: Mapped[str] = mapped_column(String(20), default=MerchantType.PERSONAL.value)
    avatar: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(String(20), default="")
    wechat: Mapped[str] = mapped_column(String(64), default="")
    province_id: Mapped[Optional[int]] = mapped_column(Integer)
    city_id: Mapped[Optional[int]] = mapped_column(Integer)
    district_id: Mapped[Optional[int]] = mapped_column(Integer)
    town_id: Mapped[Optional[int]] = mapped_column(Integer)
    village_id: Mapped[Optional[int]] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String(255), default="")
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    business_hours: Mapped[str] = mapped_column(String(128), default="")
    verify_status: Mapped[str] = mapped_column(
        String(20), default=MerchantVerifyStatus.PENDING.value, index=True
    )
    reject_reason: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    materials: Mapped[str] = mapped_column(Text, default="")  # JSON list of URLs

    user: Mapped["User"] = relationship(back_populates="merchant")
    products: Mapped[list["Product"]] = relationship(back_populates="merchant")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    cover_image: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    specs: Mapped[str] = mapped_column(Text, default="")  # free text / JSON
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    price_unit: Mapped[str] = mapped_column(String(20), default=PriceUnit.DAY.value)
    price_unit_custom: Mapped[str] = mapped_column(String(32), default="")
    deposit: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    min_rent_days: Mapped[int] = mapped_column(Integer, default=1)
    stock: Mapped[int] = mapped_column(Integer, default=1)
    province_id: Mapped[Optional[int]] = mapped_column(Integer)
    city_id: Mapped[Optional[int]] = mapped_column(Integer)
    district_id: Mapped[Optional[int]] = mapped_column(Integer)
    town_id: Mapped[Optional[int]] = mapped_column(Integer)
    village_id: Mapped[Optional[int]] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String(255), default="")
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0)
    audit_status: Mapped[str] = mapped_column(
        String(20), default=ProductAuditStatus.DRAFT.value, index=True
    )
    shelf_status: Mapped[str] = mapped_column(
        String(20), default=ProductShelfStatus.OFFLINE.value, index=True
    )
    reject_reason: Mapped[str] = mapped_column(String(255), default="")
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)

    merchant: Mapped["Merchant"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductImage(Base, TimestampMixin):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(back_populates="images")


class Favorite(Base, TimestampMixin):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uk_fav_user_target"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)


class BrowseHistory(Base, TimestampMixin):
    __tablename__ = "browse_histories"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uk_browse_user_product"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)


class Inquiry(Base, TimestampMixin):
    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), index=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"))
    type: Mapped[str] = mapped_column(String(20), nullable=False)


class Banner(Base, TimestampMixin):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), default="")
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    link_type: Mapped[str] = mapped_column(String(32), default="")  # PRODUCT/MERCHANT/URL
    link_value: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)


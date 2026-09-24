from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import (
    AdminAccount,
    Banner,
    BrowseHistory,
    Category,
    Favorite,
    FavoriteTargetType,
    Inquiry,
    InquiryType,
    Merchant,
    MerchantVerifyStatus,
    Product,
    ProductAuditStatus,
    ProductImage,
    ProductShelfStatus,
    Region,
    User,
    UserRole,
    UserStatus,
)
from app.schemas import (
    MerchantApplyIn,
    MerchantUpdateIn,
    ProductCreateIn,
    ProductUpdateIn,
    UserUpdateIn,
)


PRICE_UNIT_LABEL = {
    "HOUR": "小时",
    "DAY": "天",
    "TIME": "次",
    "MONTH": "月",
    "NEGOTIABLE": "面议",
    "CUSTOM": "自定义",
}


def public_product_filter():
    return and_(
        Product.audit_status == ProductAuditStatus.APPROVED.value,
        Product.shelf_status == ProductShelfStatus.ONLINE.value,
    )


def merchant_public_dict(m: Merchant) -> dict:
    return {
        "id": m.id,
        "merchant_name": m.merchant_name,
        "merchant_type": m.merchant_type,
        "avatar": m.avatar,
        "description": m.description,
        "phone": m.phone,
        "province_id": m.province_id,
        "city_id": m.city_id,
        "district_id": m.district_id,
        "town_id": m.town_id,
        "village_id": m.village_id,
        "address": m.address,
        "business_hours": m.business_hours,
        "verify_status": m.verify_status,
    }


def product_list_item(p: Product, merchant_name: Optional[str] = None) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "cover_image": p.cover_image,
        "price": p.price,
        "price_unit": p.price_unit,
        "price_unit_custom": p.price_unit_custom,
        "deposit": p.deposit,
        "town_id": p.town_id,
        "village_id": p.village_id,
        "address": p.address,
        "view_count": p.view_count,
        "favorite_count": p.favorite_count,
        "merchant_id": p.merchant_id,
        "merchant_name": merchant_name or (p.merchant.merchant_name if p.merchant else None),
        "category_id": p.category_id,
        "audit_status": p.audit_status,
        "shelf_status": p.shelf_status,
    }


async def wechat_code2session(code: str) -> dict:
    settings = get_settings()
    if not settings.wechat_appid or not settings.wechat_secret:
        raise AppError("未配置微信 AppID/Secret，请使用开发登录或先完成小程序注册")
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.wechat_appid,
        "secret": settings.wechat_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()
    if data.get("errcode"):
        raise AppError(f"微信登录失败: {data.get('errmsg')}")
    return data


def upsert_user_by_openid(
    db: Session,
    openid: str,
    nickname: Optional[str] = None,
    avatar: Optional[str] = None,
) -> User:
    user = db.scalar(select(User).where(User.openid == openid))
    if not user:
        user = User(
            openid=openid,
            nickname=nickname or "微信用户",
            avatar=avatar or "",
            role=UserRole.USER.value,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if nickname:
            user.nickname = nickname
        if avatar:
            user.avatar = avatar
        db.commit()
        db.refresh(user)
    return user


def issue_user_token(user: User) -> dict:
    token = create_access_token(str(user.id), role=user.role, extra={"typ": "user"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
    }


def admin_login(db: Session, username: str, password: str) -> dict:
    admin = db.scalar(select(AdminAccount).where(AdminAccount.username == username))
    if not admin or not verify_password(password, admin.password_hash):
        raise AppError("用户名或密码错误", status_code=401)
    if not admin.is_active:
        raise AppError("账号已禁用", status_code=403)
    token = create_access_token(str(admin.id), role=UserRole.ADMIN.value, extra={"typ": "admin"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": UserRole.ADMIN.value,
        "user_id": admin.user_id or 0,
    }


def update_user(db: Session, user: User, data: UserUpdateIn) -> User:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


def build_category_tree(rows: List[Category]) -> List[dict]:
    by_parent: dict[Optional[int], List[Category]] = {}
    for c in rows:
        by_parent.setdefault(c.parent_id, []).append(c)

    def walk(parent_id: Optional[int]) -> List[dict]:
        items = sorted(by_parent.get(parent_id, []), key=lambda x: (x.sort, x.id))
        return [
            {
                "id": c.id,
                "parent_id": c.parent_id,
                "name": c.name,
                "icon": c.icon,
                "sort": c.sort,
                "status": c.status,
                "children": walk(c.id),
            }
            for c in items
        ]

    return walk(None)


def list_regions(db: Session, parent_id: Optional[int] = None) -> List[Region]:
    stmt = select(Region).where(Region.status == 1)
    if parent_id is None:
        stmt = stmt.where(Region.parent_id.is_(None))
    else:
        stmt = stmt.where(Region.parent_id == parent_id)
    stmt = stmt.order_by(Region.sort, Region.id)
    return list(db.scalars(stmt).all())


def apply_merchant(db: Session, user: User, data: MerchantApplyIn) -> Merchant:
    existing = db.scalar(select(Merchant).where(Merchant.user_id == user.id))
    if existing and existing.verify_status == MerchantVerifyStatus.APPROVED.value:
        raise AppError("已是认证商家，无需重复申请")
    if existing and existing.verify_status == MerchantVerifyStatus.PENDING.value:
        raise AppError("入驻申请审核中，请耐心等待")

    payload = data.model_dump()
    materials = json.dumps(payload.pop("materials") or [], ensure_ascii=False)
    if existing:
        for k, v in payload.items():
            setattr(existing, k, v)
        existing.materials = materials
        existing.verify_status = MerchantVerifyStatus.PENDING.value
        existing.reject_reason = ""
        merchant = existing
    else:
        merchant = Merchant(user_id=user.id, materials=materials, **payload)
        db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant


def get_my_merchant(db: Session, user: User) -> Optional[Merchant]:
    return db.scalar(select(Merchant).where(Merchant.user_id == user.id))


def update_merchant_profile(db: Session, merchant: Merchant, data: MerchantUpdateIn) -> Merchant:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(merchant, k, v)
    db.commit()
    db.refresh(merchant)
    return merchant


def ensure_approved_merchant(db: Session, user: User) -> Merchant:
    merchant = get_my_merchant(db, user)
    if not merchant:
        raise AppError("请先申请商家入驻")
    if merchant.verify_status != MerchantVerifyStatus.APPROVED.value:
        raise AppError("商家尚未通过审核，无法发布商品")
    return merchant


def _apply_product_fields(
    product: Product, data: ProductCreateIn | ProductUpdateIn, *, partial: bool = False
) -> None:
    dump = data.model_dump(exclude={"images", "submit"}, exclude_unset=partial)
    for k, v in dump.items():
        if partial and v is None and k not in ("price", "deposit"):
            continue
        setattr(product, k, v)


def create_product(db: Session, merchant: Merchant, data: ProductCreateIn) -> Product:
    product = Product(merchant_id=merchant.id)
    _apply_product_fields(product, data)
    if data.submit:
        product.audit_status = ProductAuditStatus.PENDING_REVIEW.value
        product.shelf_status = ProductShelfStatus.OFFLINE.value
    else:
        product.audit_status = ProductAuditStatus.DRAFT.value
        product.shelf_status = ProductShelfStatus.OFFLINE.value
    db.add(product)
    db.flush()
    for img in data.images:
        db.add(ProductImage(product_id=product.id, image_url=img.image_url, sort=img.sort))
    if not product.cover_image and data.images:
        product.cover_image = data.images[0].image_url
    db.commit()
    db.refresh(product)
    return product


def update_product(
    db: Session, merchant: Merchant, product_id: int, data: ProductUpdateIn
) -> Product:
    product = db.get(Product, product_id)
    if not product or product.merchant_id != merchant.id:
        raise AppError("商品不存在", status_code=404)
    _apply_product_fields(product, data, partial=True)
    if data.images is not None:
        for old in list(product.images):
            db.delete(old)
        db.flush()
        for img in data.images:
            db.add(ProductImage(product_id=product.id, image_url=img.image_url, sort=img.sort))
        if data.images and (not product.cover_image or data.cover_image is not None):
            if data.cover_image:
                product.cover_image = data.cover_image
            elif data.images:
                product.cover_image = data.images[0].image_url
    if data.submit:
        product.audit_status = ProductAuditStatus.PENDING_REVIEW.value
        product.reject_reason = ""
    db.commit()
    db.refresh(product)
    return product


def submit_product(db: Session, merchant: Merchant, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product or product.merchant_id != merchant.id:
        raise AppError("商品不存在", status_code=404)
    product.audit_status = ProductAuditStatus.PENDING_REVIEW.value
    product.reject_reason = ""
    db.commit()
    db.refresh(product)
    return product


def set_product_shelf(
    db: Session, merchant: Merchant, product_id: int, online: bool
) -> Product:
    product = db.get(Product, product_id)
    if not product or product.merchant_id != merchant.id:
        raise AppError("商品不存在", status_code=404)
    if online:
        if product.audit_status != ProductAuditStatus.APPROVED.value:
            raise AppError("仅审核通过的商品可上架")
        product.shelf_status = ProductShelfStatus.ONLINE.value
    else:
        product.shelf_status = ProductShelfStatus.OFFLINE.value
    db.commit()
    db.refresh(product)
    return product


def query_products(
    db: Session,
    *,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    province_id: Optional[int] = None,
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    town_id: Optional[int] = None,
    village_id: Optional[int] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    merchant_id: Optional[int] = None,
    public_only: bool = True,
    page: int = 1,
    page_size: int = 20,
):
    stmt = select(Product).options(selectinload(Product.merchant))
    if public_only:
        stmt = stmt.where(public_product_filter())
        stmt = stmt.join(Merchant).where(
            Merchant.verify_status == MerchantVerifyStatus.APPROVED.value,
            Merchant.status == "ACTIVE",
        )
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(Product.name.like(like), Product.description.like(like)))
    if category_id:
        # include children categories
        child_ids = list(
            db.scalars(select(Category.id).where(Category.parent_id == category_id)).all()
        )
        ids = [category_id] + child_ids
        stmt = stmt.where(Product.category_id.in_(ids))
    if province_id:
        stmt = stmt.where(Product.province_id == province_id)
    if city_id:
        stmt = stmt.where(Product.city_id == city_id)
    if district_id:
        stmt = stmt.where(Product.district_id == district_id)
    if town_id:
        stmt = stmt.where(Product.town_id == town_id)
    if village_id:
        stmt = stmt.where(Product.village_id == village_id)
    if merchant_id:
        stmt = stmt.where(Product.merchant_id == merchant_id)
    if price_min is not None:
        stmt = stmt.where(Product.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(Product.price <= price_max)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0
    rows = list(
        db.scalars(
            stmt.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
    )
    return rows, total


def get_product_detail(
    db: Session, product_id: int, user: Optional[User] = None, allow_owner: bool = False
) -> dict:
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.images), selectinload(Product.merchant))
        .where(Product.id == product_id)
    )
    if not product:
        raise AppError("商品不存在", status_code=404)

    is_owner = bool(
        user and product.merchant and product.merchant.user_id == user.id
    )
    is_public = (
        product.audit_status == ProductAuditStatus.APPROVED.value
        and product.shelf_status == ProductShelfStatus.ONLINE.value
    )
    if not is_public and not (allow_owner and is_owner) and not (
        user and user.role == UserRole.ADMIN.value
    ):
        raise AppError("商品不存在或已下架", status_code=404)

    product.view_count += 1
    if user:
        hist = db.scalar(
            select(BrowseHistory).where(
                BrowseHistory.user_id == user.id, BrowseHistory.product_id == product.id
            )
        )
        if hist:
            hist.updated_at = datetime.now(timezone.utc)
        else:
            db.add(BrowseHistory(user_id=user.id, product_id=product.id))
    db.commit()
    db.refresh(product)

    favorited = False
    if user:
        favorited = (
            db.scalar(
                select(Favorite.id).where(
                    Favorite.user_id == user.id,
                    Favorite.target_type == FavoriteTargetType.PRODUCT.value,
                    Favorite.target_id == product.id,
                )
            )
            is not None
        )

    return {
        "id": product.id,
        "merchant_id": product.merchant_id,
        "category_id": product.category_id,
        "name": product.name,
        "cover_image": product.cover_image,
        "description": product.description,
        "specs": product.specs,
        "price": product.price,
        "price_unit": product.price_unit,
        "price_unit_custom": product.price_unit_custom,
        "deposit": product.deposit,
        "min_rent_days": product.min_rent_days,
        "stock": product.stock,
        "province_id": product.province_id,
        "city_id": product.city_id,
        "district_id": product.district_id,
        "town_id": product.town_id,
        "village_id": product.village_id,
        "address": product.address,
        "view_count": product.view_count,
        "favorite_count": product.favorite_count,
        "images": [
            {"id": i.id, "image_url": i.image_url, "sort": i.sort}
            for i in sorted(product.images, key=lambda x: x.sort)
        ],
        "merchant": merchant_public_dict(product.merchant) if product.merchant else None,
        "is_favorited": favorited,
        "audit_status": product.audit_status if is_owner else None,
        "shelf_status": product.shelf_status if is_owner else None,
        "reject_reason": product.reject_reason if is_owner else None,
    }


def toggle_favorite(db: Session, user: User, target_type: str, target_id: int, add: bool):
    if target_type not in (
        FavoriteTargetType.PRODUCT.value,
        FavoriteTargetType.MERCHANT.value,
    ):
        raise AppError("无效的收藏类型")
    existing = db.scalar(
        select(Favorite).where(
            Favorite.user_id == user.id,
            Favorite.target_type == target_type,
            Favorite.target_id == target_id,
        )
    )
    if add:
        if existing:
            return existing
        fav = Favorite(user_id=user.id, target_type=target_type, target_id=target_id)
        db.add(fav)
        if target_type == FavoriteTargetType.PRODUCT.value:
            product = db.get(Product, target_id)
            if product:
                product.favorite_count += 1
        db.commit()
        return fav
    if existing:
        db.delete(existing)
        if target_type == FavoriteTargetType.PRODUCT.value:
            product = db.get(Product, target_id)
            if product and product.favorite_count > 0:
                product.favorite_count -= 1
        db.commit()
    return None


def record_inquiry(
    db: Session,
    *,
    user: Optional[User],
    merchant_id: int,
    product_id: Optional[int],
    inquiry_type: str,
) -> Inquiry:
    row = Inquiry(
        user_id=user.id if user else None,
        merchant_id=merchant_id,
        product_id=product_id,
        type=inquiry_type,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_home(db: Session) -> dict:
    banners = list(
        db.scalars(
            select(Banner).where(Banner.status == 1).order_by(Banner.sort, Banner.id.desc())
        ).all()
    )
    hot_products, _ = query_products(db, page=1, page_size=10)
    # sort by view for hot
    hot_products = sorted(hot_products, key=lambda p: p.view_count, reverse=True)[:8]
    merchants = list(
        db.scalars(
            select(Merchant)
            .where(
                Merchant.verify_status == MerchantVerifyStatus.APPROVED.value,
                Merchant.status == "ACTIVE",
            )
            .order_by(Merchant.id.desc())
            .limit(6)
        ).all()
    )
    recommended, _ = query_products(db, page=1, page_size=20)
    recommended = [p for p in recommended if p.is_recommended][:8]
    if not recommended:
        recommended = hot_products[:4]
    return {
        "banners": [
            {
                "id": b.id,
                "title": b.title,
                "image_url": b.image_url,
                "link_type": b.link_type,
                "link_value": b.link_value,
                "sort": b.sort,
            }
            for b in banners
        ],
        "hot_products": [product_list_item(p) for p in hot_products],
        "recommended_products": [product_list_item(p) for p in recommended],
        "recommended_merchants": [merchant_public_dict(m) for m in merchants],
        "categories": build_category_tree(
            list(db.scalars(select(Category).where(Category.status == 1)).all())
        )[:8],
    }


def dashboard_stats(db: Session) -> dict:
    return {
        "user_count": db.scalar(select(func.count()).select_from(User)) or 0,
        "merchant_count": db.scalar(select(func.count()).select_from(Merchant)) or 0,
        "product_count": db.scalar(select(func.count()).select_from(Product)) or 0,
        "pending_merchants": db.scalar(
            select(func.count()).select_from(Merchant).where(
                Merchant.verify_status == MerchantVerifyStatus.PENDING.value
            )
        )
        or 0,
        "pending_products": db.scalar(
            select(func.count())
            .select_from(Product)
            .where(Product.audit_status == ProductAuditStatus.PENDING_REVIEW.value)
        )
        or 0,
        "view_count": db.scalar(select(func.coalesce(func.sum(Product.view_count), 0))) or 0,
        "favorite_count": db.scalar(select(func.count()).select_from(Favorite)) or 0,
        "inquiry_count": db.scalar(select(func.count()).select_from(Inquiry)) or 0,
    }


def ensure_admin_seed(db: Session) -> None:
    settings = get_settings()
    admin = db.scalar(
        select(AdminAccount).where(AdminAccount.username == settings.admin_seed_username)
    )
    if admin:
        return
    user = User(
        openid=f"admin_{settings.admin_seed_username}",
        nickname="平台管理员",
        role=UserRole.ADMIN.value,
    )
    db.add(user)
    db.flush()
    db.add(
        AdminAccount(
            username=settings.admin_seed_username,
            password_hash=hash_password(settings.admin_seed_password),
            user_id=user.id,
        )
    )
    db.commit()

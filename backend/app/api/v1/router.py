from typing import Optional

from fastapi import APIRouter, File, Query, UploadFile

from app.api.deps import AdminDep, DbDep, MerchantUserDep, OptionalUserDep, UserDep
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.response import ok
from app.models import (
    Banner,
    BrowseHistory,
    Category,
    Favorite,
    FavoriteTargetType,
    Merchant,
    MerchantVerifyStatus,
    Product,
    ProductAuditStatus,
    ProductShelfStatus,
    Region,
    User,
    UserRole,
    UserStatus,
)
from app.schemas import (
    AdminLoginIn,
    AuditIn,
    BannerIn,
    CategoryCreateIn,
    CategoryUpdateIn,
    DevLoginIn,
    FavoriteIn,
    MerchantApplyIn,
    MerchantUpdateIn,
    ProductCreateIn,
    ProductUpdateIn,
    RegionCreateIn,
    UserUpdateIn,
    WechatLoginIn,
)
from app.services import biz
from app.services.storage import get_storage
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter()


# ---------- auth ----------
@router.post("/auth/wechat/login")
async def wechat_login(body: WechatLoginIn, db: DbDep):
    data = await biz.wechat_code2session(body.code)
    openid = data["openid"]
    user = biz.upsert_user_by_openid(db, openid, body.nickname, body.avatar)
    return ok(biz.issue_user_token(user))


@router.post("/auth/dev/login")
def dev_login(body: DevLoginIn, db: DbDep):
    if not get_settings().is_local:
        raise AppError("生产环境禁用开发登录", status_code=403)
    user = biz.upsert_user_by_openid(db, body.openid, body.nickname, body.avatar)
    return ok(biz.issue_user_token(user))


@router.get("/users/me")
def get_me(user: UserDep, db: DbDep):
    merchant = biz.get_my_merchant(db, user)
    return ok(
        {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "phone": user.phone,
            "role": user.role,
            "status": user.status,
            "merchant": (
                {
                    "id": merchant.id,
                    "verify_status": merchant.verify_status,
                    "merchant_name": merchant.merchant_name,
                    "reject_reason": merchant.reject_reason,
                }
                if merchant
                else None
            ),
        }
    )


@router.put("/users/me")
def update_me(body: UserUpdateIn, user: UserDep, db: DbDep):
    u = biz.update_user(db, user, body)
    return ok(
        {
            "id": u.id,
            "nickname": u.nickname,
            "avatar": u.avatar,
            "phone": u.phone,
            "role": u.role,
            "status": u.status,
        }
    )


@router.post("/uploads")
async def upload_file(user: UserDep, file: UploadFile = File(...)):
    url = get_storage().save(file)
    return ok({"url": url})


# ---------- home / category / region ----------
@router.get("/home")
def home(db: DbDep):
    return ok(biz.get_home(db))


@router.get("/categories")
def categories(db: DbDep):
    rows = list(db.scalars(select(Category).where(Category.status == 1)).all())
    return ok(biz.build_category_tree(rows))


@router.get("/regions")
def regions(db: DbDep, parent_id: Optional[int] = None):
    rows = biz.list_regions(db, parent_id)
    return ok(
        [
            {
                "id": r.id,
                "parent_id": r.parent_id,
                "name": r.name,
                "level": r.level,
                "code": r.code,
                "sort": r.sort,
                "status": r.status,
            }
            for r in rows
        ]
    )


# ---------- products ----------
@router.get("/products")
def list_products(
    db: DbDep,
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
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    rows, total = biz.query_products(
        db,
        keyword=keyword,
        category_id=category_id,
        province_id=province_id,
        city_id=city_id,
        district_id=district_id,
        town_id=town_id,
        village_id=village_id,
        price_min=price_min,
        price_max=price_max,
        merchant_id=merchant_id,
        page=page,
        page_size=page_size,
    )
    return ok(
        {
            "items": [biz.product_list_item(p) for p in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/search/products")
def search_products(
    db: DbDep,
    keyword: str = "",
    category_id: Optional[int] = None,
    province_id: Optional[int] = None,
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    town_id: Optional[int] = None,
    village_id: Optional[int] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    rows, total = biz.query_products(
        db,
        keyword=keyword or None,
        category_id=category_id,
        province_id=province_id,
        city_id=city_id,
        district_id=district_id,
        town_id=town_id,
        village_id=village_id,
        price_min=price_min,
        price_max=price_max,
        page=page,
        page_size=page_size,
    )
    return ok(
        {
            "items": [biz.product_list_item(p) for p in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/products/{product_id}")
def product_detail(product_id: int, db: DbDep, user: OptionalUserDep):
    return ok(biz.get_product_detail(db, product_id, user, allow_owner=True))


# ---------- merchants ----------
@router.post("/merchants/apply")
def merchant_apply(body: MerchantApplyIn, user: UserDep, db: DbDep):
    m = biz.apply_merchant(db, user, body)
    return ok(
        {
            "id": m.id,
            "verify_status": m.verify_status,
            "merchant_name": m.merchant_name,
        }
    )


@router.get("/merchants/me")
def merchant_me(user: UserDep, db: DbDep):
    m = biz.get_my_merchant(db, user)
    if not m:
        return ok(None)
    data = biz.merchant_public_dict(m)
    data.update(
        {
            "wechat": m.wechat,
            "reject_reason": m.reject_reason,
            "materials": m.materials,
            "user_id": m.user_id,
        }
    )
    return ok(data)


@router.put("/merchants/me")
def merchant_update(body: MerchantUpdateIn, user: UserDep, db: DbDep):
    m = biz.get_my_merchant(db, user)
    if not m:
        raise AppError("商家不存在")
    m = biz.update_merchant_profile(db, m, body)
    data = biz.merchant_public_dict(m)
    data["wechat"] = m.wechat
    return ok(data)


@router.get("/merchants/{merchant_id}")
def merchant_detail(merchant_id: int, db: DbDep):
    m = db.get(Merchant, merchant_id)
    if not m or m.verify_status != MerchantVerifyStatus.APPROVED.value:
        raise AppError("商家不存在", status_code=404)
    return ok(biz.merchant_public_dict(m))


@router.get("/merchants/{merchant_id}/products")
def merchant_products(
    merchant_id: int,
    db: DbDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    rows, total = biz.query_products(
        db, merchant_id=merchant_id, page=page, page_size=page_size
    )
    return ok(
        {
            "items": [biz.product_list_item(p) for p in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.post("/merchants/{merchant_id}/contact/phone")
def contact_phone(
    merchant_id: int,
    db: DbDep,
    user: OptionalUserDep,
    product_id: Optional[int] = None,
):
    m = db.get(Merchant, merchant_id)
    if not m:
        raise AppError("商家不存在", status_code=404)
    biz.record_inquiry(
        db, user=user, merchant_id=merchant_id, product_id=product_id, inquiry_type="PHONE"
    )
    return ok({"phone": m.phone})


@router.post("/merchants/{merchant_id}/contact/wechat")
def contact_wechat(
    merchant_id: int,
    db: DbDep,
    user: UserDep,
    product_id: Optional[int] = None,
):
    m = db.get(Merchant, merchant_id)
    if not m:
        raise AppError("商家不存在", status_code=404)
    if not m.wechat:
        raise AppError("商家未设置微信号")
    biz.record_inquiry(
        db, user=user, merchant_id=merchant_id, product_id=product_id, inquiry_type="WECHAT"
    )
    return ok({"wechat": m.wechat})


# ---------- merchant products ----------
@router.post("/merchants/me/products")
def create_my_product(body: ProductCreateIn, user: MerchantUserDep, db: DbDep):
    merchant = biz.ensure_approved_merchant(db, user)
    p = biz.create_product(db, merchant, body)
    return ok({"id": p.id, "audit_status": p.audit_status})


@router.put("/merchants/me/products/{product_id}")
def update_my_product(
    product_id: int, body: ProductUpdateIn, user: MerchantUserDep, db: DbDep
):
    merchant = biz.ensure_approved_merchant(db, user)
    p = biz.update_product(db, merchant, product_id, body)
    return ok({"id": p.id, "audit_status": p.audit_status})


@router.post("/merchants/me/products/{product_id}/submit")
def submit_my_product(product_id: int, user: MerchantUserDep, db: DbDep):
    merchant = biz.ensure_approved_merchant(db, user)
    p = biz.submit_product(db, merchant, product_id)
    return ok({"id": p.id, "audit_status": p.audit_status})


@router.post("/merchants/me/products/{product_id}/online")
def online_my_product(product_id: int, user: MerchantUserDep, db: DbDep):
    merchant = biz.ensure_approved_merchant(db, user)
    p = biz.set_product_shelf(db, merchant, product_id, True)
    return ok({"id": p.id, "shelf_status": p.shelf_status})


@router.post("/merchants/me/products/{product_id}/offline")
def offline_my_product(product_id: int, user: MerchantUserDep, db: DbDep):
    merchant = biz.ensure_approved_merchant(db, user)
    p = biz.set_product_shelf(db, merchant, product_id, False)
    return ok({"id": p.id, "shelf_status": p.shelf_status})


@router.get("/merchants/me/products")
def list_my_products(
    user: MerchantUserDep,
    db: DbDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    merchant = biz.get_my_merchant(db, user)
    if not merchant:
        raise AppError("商家不存在")
    rows, total = biz.query_products(
        db, merchant_id=merchant.id, public_only=False, page=page, page_size=page_size
    )
    return ok(
        {
            "items": [biz.product_list_item(p) for p in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


# ---------- favorites / history ----------
@router.post("/favorites")
def add_favorite(body: FavoriteIn, user: UserDep, db: DbDep):
    biz.toggle_favorite(db, user, body.target_type, body.target_id, True)
    return ok(True)


@router.delete("/favorites")
def remove_favorite(
    user: UserDep,
    db: DbDep,
    target_type: str,
    target_id: int,
):
    biz.toggle_favorite(db, user, target_type, target_id, False)
    return ok(True)


@router.get("/favorites")
def list_favorites(user: UserDep, db: DbDep, target_type: Optional[str] = None):
    stmt = select(Favorite).where(Favorite.user_id == user.id)
    if target_type:
        stmt = stmt.where(Favorite.target_type == target_type)
    favs = list(db.scalars(stmt.order_by(Favorite.id.desc())).all())
    items = []
    for f in favs:
        if f.target_type == FavoriteTargetType.PRODUCT.value:
            p = db.scalar(
                select(Product)
                .options(selectinload(Product.merchant))
                .where(Product.id == f.target_id)
            )
            if p:
                items.append({"target_type": f.target_type, "product": biz.product_list_item(p)})
        else:
            m = db.get(Merchant, f.target_id)
            if m:
                items.append(
                    {"target_type": f.target_type, "merchant": biz.merchant_public_dict(m)}
                )
    return ok(items)


@router.get("/browse-history")
def browse_history(user: UserDep, db: DbDep):
    rows = list(
        db.scalars(
            select(BrowseHistory)
            .where(BrowseHistory.user_id == user.id)
            .order_by(BrowseHistory.updated_at.desc())
            .limit(50)
        ).all()
    )
    items = []
    for h in rows:
        p = db.scalar(
            select(Product)
            .options(selectinload(Product.merchant))
            .where(Product.id == h.product_id)
        )
        if p:
            items.append(biz.product_list_item(p))
    return ok(items)


# ---------- admin ----------
admin_router = APIRouter(prefix="/admin")


@admin_router.post("/auth/login")
def admin_login(body: AdminLoginIn, db: DbDep):
    return ok(biz.admin_login(db, body.username, body.password))


@admin_router.get("/dashboard/stats")
def admin_stats(_: AdminDep, db: DbDep):
    return ok(biz.dashboard_stats(db))


@admin_router.get("/users")
def admin_users(
    _: AdminDep,
    db: DbDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    from sqlalchemy import func

    total = db.scalar(select(func.count()).select_from(User)) or 0
    rows = list(
        db.scalars(
            select(User).order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
    )
    return ok(
        {
            "items": [
                {
                    "id": u.id,
                    "nickname": u.nickname,
                    "avatar": u.avatar,
                    "phone": u.phone,
                    "role": u.role,
                    "status": u.status,
                    "openid": u.openid,
                }
                for u in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@admin_router.post("/users/{user_id}/status")
def admin_user_status(user_id: int, status: str, _: AdminDep, db: DbDep):
    u = db.get(User, user_id)
    if not u:
        raise AppError("用户不存在", status_code=404)
    if status not in (UserStatus.ACTIVE.value, UserStatus.DISABLED.value):
        raise AppError("无效状态")
    u.status = status
    db.commit()
    return ok(True)


@admin_router.get("/merchants")
def admin_merchants(
    _: AdminDep,
    db: DbDep,
    verify_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    from sqlalchemy import func

    stmt = select(Merchant)
    if verify_status:
        stmt = stmt.where(Merchant.verify_status == verify_status)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        db.scalars(
            stmt.order_by(Merchant.id.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
    )
    return ok(
        {
            "items": [
                {
                    **biz.merchant_public_dict(m),
                    "wechat": m.wechat,
                    "reject_reason": m.reject_reason,
                    "materials": m.materials,
                    "user_id": m.user_id,
                }
                for m in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@admin_router.post("/merchants/{merchant_id}/audit")
def admin_merchant_audit(merchant_id: int, body: AuditIn, _: AdminDep, db: DbDep):
    m = db.get(Merchant, merchant_id)
    if not m:
        raise AppError("商家不存在", status_code=404)
    if body.action == "approve":
        m.verify_status = MerchantVerifyStatus.APPROVED.value
        m.reject_reason = ""
        user = db.get(User, m.user_id)
        if user and user.role == UserRole.USER.value:
            user.role = UserRole.MERCHANT.value
    elif body.action == "reject":
        m.verify_status = MerchantVerifyStatus.REJECTED.value
        m.reject_reason = body.reason or "审核未通过"
    else:
        raise AppError("action 应为 approve 或 reject")
    db.commit()
    return ok(True)


@admin_router.get("/products")
def admin_products(
    _: AdminDep,
    db: DbDep,
    audit_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    from sqlalchemy import func

    stmt = select(Product).options(selectinload(Product.merchant))
    if audit_status:
        stmt = stmt.where(Product.audit_status == audit_status)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        db.scalars(
            stmt.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
    )
    return ok(
        {
            "items": [biz.product_list_item(p) for p in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@admin_router.post("/products/{product_id}/audit")
def admin_product_audit(product_id: int, body: AuditIn, _: AdminDep, db: DbDep):
    p = db.get(Product, product_id)
    if not p:
        raise AppError("商品不存在", status_code=404)
    if body.action == "approve":
        p.audit_status = ProductAuditStatus.APPROVED.value
        p.shelf_status = ProductShelfStatus.ONLINE.value
        p.reject_reason = ""
    elif body.action == "reject":
        p.audit_status = ProductAuditStatus.REJECTED.value
        p.shelf_status = ProductShelfStatus.OFFLINE.value
        p.reject_reason = body.reason or "审核未通过"
    else:
        raise AppError("action 应为 approve 或 reject")
    db.commit()
    return ok(True)


@admin_router.post("/products/{product_id}/offline")
def admin_product_offline(product_id: int, _: AdminDep, db: DbDep):
    p = db.get(Product, product_id)
    if not p:
        raise AppError("商品不存在", status_code=404)
    p.shelf_status = ProductShelfStatus.OFFLINE.value
    db.commit()
    return ok(True)


@admin_router.post("/products/{product_id}/recommend")
def admin_product_recommend(
    product_id: int, _: AdminDep, db: DbDep, recommended: bool = True
):
    p = db.get(Product, product_id)
    if not p:
        raise AppError("商品不存在", status_code=404)
    p.is_recommended = recommended
    db.commit()
    return ok(True)


@admin_router.get("/categories")
def admin_categories(_: AdminDep, db: DbDep):
    rows = list(db.scalars(select(Category)).all())
    return ok(biz.build_category_tree(rows))


@admin_router.post("/categories")
def admin_create_category(body: CategoryCreateIn, _: AdminDep, db: DbDep):
    c = Category(**body.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return ok({"id": c.id})


@admin_router.put("/categories/{category_id}")
def admin_update_category(
    category_id: int, body: CategoryUpdateIn, _: AdminDep, db: DbDep
):
    c = db.get(Category, category_id)
    if not c:
        raise AppError("分类不存在", status_code=404)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    return ok(True)


@admin_router.delete("/categories/{category_id}")
def admin_delete_category(category_id: int, _: AdminDep, db: DbDep):
    c = db.get(Category, category_id)
    if not c:
        raise AppError("分类不存在", status_code=404)
    db.delete(c)
    db.commit()
    return ok(True)


@admin_router.get("/regions")
def admin_regions(_: AdminDep, db: DbDep, parent_id: Optional[int] = None):
    rows = biz.list_regions(db, parent_id)
    # also allow listing disabled in admin? MVP reuse public filter status=1
    # Better: list all children for admin
    stmt = select(Region)
    if parent_id is None:
        stmt = stmt.where(Region.parent_id.is_(None))
    else:
        stmt = stmt.where(Region.parent_id == parent_id)
    rows = list(db.scalars(stmt.order_by(Region.sort, Region.id)).all())
    return ok(
        [
            {
                "id": r.id,
                "parent_id": r.parent_id,
                "name": r.name,
                "level": r.level,
                "code": r.code,
                "sort": r.sort,
                "status": r.status,
            }
            for r in rows
        ]
    )


@admin_router.post("/regions")
def admin_create_region(body: RegionCreateIn, _: AdminDep, db: DbDep):
    r = Region(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return ok({"id": r.id})


@admin_router.put("/regions/{region_id}")
def admin_update_region(region_id: int, body: RegionCreateIn, _: AdminDep, db: DbDep):
    r = db.get(Region, region_id)
    if not r:
        raise AppError("地区不存在", status_code=404)
    for k, v in body.model_dump().items():
        setattr(r, k, v)
    db.commit()
    return ok(True)


@admin_router.get("/banners")
def admin_banners(_: AdminDep, db: DbDep):
    rows = list(db.scalars(select(Banner).order_by(Banner.sort, Banner.id.desc())).all())
    return ok(
        [
            {
                "id": b.id,
                "title": b.title,
                "image_url": b.image_url,
                "link_type": b.link_type,
                "link_value": b.link_value,
                "sort": b.sort,
                "status": b.status,
            }
            for b in rows
        ]
    )


@admin_router.post("/banners")
def admin_create_banner(body: BannerIn, _: AdminDep, db: DbDep):
    b = Banner(**body.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    return ok({"id": b.id})


@admin_router.put("/banners/{banner_id}")
def admin_update_banner(banner_id: int, body: BannerIn, _: AdminDep, db: DbDep):
    b = db.get(Banner, banner_id)
    if not b:
        raise AppError("Banner 不存在", status_code=404)
    for k, v in body.model_dump().items():
        setattr(b, k, v)
    db.commit()
    return ok(True)


@admin_router.delete("/banners/{banner_id}")
def admin_delete_banner(banner_id: int, _: AdminDep, db: DbDep):
    b = db.get(Banner, banner_id)
    if not b:
        raise AppError("Banner 不存在", status_code=404)
    db.delete(b)
    db.commit()
    return ok(True)

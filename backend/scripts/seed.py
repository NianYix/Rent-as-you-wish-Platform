"""Database seed: admin + categories + regions (+ optional demo data)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models import (
    Banner,
    Category,
    Merchant,
    MerchantVerifyStatus,
    PriceUnit,
    Product,
    ProductAuditStatus,
    ProductImage,
    ProductShelfStatus,
    Region,
    User,
    UserRole,
)
from app.services.biz import ensure_admin_seed


def seed_categories(db):
    if db.scalar(select(Category).limit(1)):
        return
    tree = [
        (
            "婚庆活动",
            ["桌椅", "帐篷", "舞台", "音响", "灯光", "婚庆用品"],
        ),
        (
            "机械设备",
            ["挖掘机", "装载机", "发电机", "电焊机", "其他设备"],
        ),
        (
            "农业工具",
            ["收割机", "播种机", "打药机", "抽水机", "农用工具"],
        ),
        (
            "生活用品",
            ["空调", "冰柜", "厨房设备", "其他"],
        ),
        (
            "车辆",
            ["婚车", "货车", "工程车辆", "其他"],
        ),
        ("其他", ["综合"]),
    ]
    sort = 0
    for name, children in tree:
        sort += 1
        parent = Category(name=name, sort=sort, icon="")
        db.add(parent)
        db.flush()
        for i, child in enumerate(children, start=1):
            db.add(Category(parent_id=parent.id, name=child, sort=i))
    db.commit()
    print("categories seeded")


def seed_regions(db):
    if db.scalar(select(Region).limit(1)):
        return
    # Demo: 示例省/市/区县/乡镇（村级结构预留，可后台补录）
    province = Region(name="示例省", level=1, code="990000", sort=1)
    db.add(province)
    db.flush()
    city = Region(parent_id=province.id, name="示例市", level=2, code="990100", sort=1)
    db.add(city)
    db.flush()
    districts = [
        ("示例县", "990101"),
        ("邻县", "990102"),
    ]
    town_names = [
        ("东风镇", "幸福乡", "青山镇", "河畔镇"),
        ("柳林镇", "金桥乡", "南湾镇"),
    ]
    for di, (dname, dcode) in enumerate(districts):
        district = Region(
            parent_id=city.id, name=dname, level=3, code=dcode, sort=di + 1
        )
        db.add(district)
        db.flush()
        for ti, tname in enumerate(town_names[di]):
            town = Region(
                parent_id=district.id,
                name=tname,
                level=4,
                code=f"{dcode}{ti+1:03d}",
                sort=ti + 1,
            )
            db.add(town)
            db.flush()
            # one sample village under first town only (structure demo)
            if di == 0 and ti == 0:
                db.add(
                    Region(
                        parent_id=town.id,
                        name="示范村",
                        level=5,
                        code=f"{dcode}{ti+1:03d}001",
                        sort=1,
                    )
                )
    db.commit()
    print("regions seeded (to town + sample village)")


def seed_demo(db):
    if db.scalar(select(Product).limit(1)):
        return
    # demo merchant user
    user = db.scalar(select(User).where(User.openid == "demo_merchant_openid"))
    if not user:
        user = User(
            openid="demo_merchant_openid",
            nickname="演示商家账号",
            role=UserRole.MERCHANT.value,
        )
        db.add(user)
        db.flush()
    town = db.scalar(select(Region).where(Region.level == 4).limit(1))
    village = db.scalar(select(Region).where(Region.level == 5).limit(1))
    district = db.get(Region, town.parent_id) if town else None
    city = db.get(Region, district.parent_id) if district else None
    province = db.get(Region, city.parent_id) if city else None
    cat = db.scalar(select(Category).where(Category.parent_id.is_not(None)).limit(1))
    merchant = db.scalar(select(Merchant).where(Merchant.user_id == user.id))
    if not merchant:
        merchant = Merchant(
            user_id=user.id,
            merchant_name="东风镇便民租赁",
            phone="13800000000",
            wechat="dongfeng_rent",
            description="乡镇本地租赁商家，桌椅帐篷机械均可租。",
            province_id=province.id if province else None,
            city_id=city.id if city else None,
            district_id=district.id if district else None,
            town_id=town.id if town else None,
            village_id=village.id if village else None,
            address="东风镇集市路口",
            business_hours="08:00-20:00",
            verify_status=MerchantVerifyStatus.APPROVED.value,
        )
        db.add(merchant)
        db.flush()
    products = [
        ("大型婚庆帐篷", "DAY", 100, 300, "适合农村婚礼宴席，约容纳 200 人。"),
        ("折叠桌椅套装", "DAY", 2, 0, "桌椅按把/天计价，支持批量租赁。"),
        ("专业音响设备", "DAY", 150, 200, "含话筒与简易搭建指导。"),
    ]
    for name, unit, price, deposit, desc in products:
        p = Product(
            merchant_id=merchant.id,
            category_id=cat.id if cat else 1,
            name=name,
            cover_image="",
            description=desc,
            specs="详见现场确认",
            price=price,
            price_unit=unit,
            deposit=deposit,
            stock=10,
            province_id=merchant.province_id,
            city_id=merchant.city_id,
            district_id=merchant.district_id,
            town_id=merchant.town_id,
            village_id=merchant.village_id,
            address=merchant.address,
            audit_status=ProductAuditStatus.APPROVED.value,
            shelf_status=ProductShelfStatus.ONLINE.value,
            is_recommended=True,
        )
        db.add(p)
    if not db.scalar(select(Banner).limit(1)):
        db.add(
            Banner(
                title="乡镇物品租赁",
                image_url="https://via.placeholder.com/750x300?text=Rent+Local",
                link_type="",
                link_value="",
                sort=1,
            )
        )
    db.commit()
    print("demo merchant/products seeded")


def main():
    print("creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_admin_seed(db)
        print("admin seeded")
        seed_categories(db)
        seed_regions(db)
        seed_demo(db)
        print("done")
    finally:
        db.close()


if __name__ == "__main__":
    main()

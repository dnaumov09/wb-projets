from .model import Seller, SellerUser, SellerDatabase, DatabaseUser, session

BLOOMSTORM_SID = 'cd079a55-56e9-454f-bb41-cdb030894913'


def get_all_sellers() -> list[Seller]:
    return session.query(Seller).all()


def get_my_seller() -> Seller:
    return session.query(Seller).filter(Seller.sid == BLOOMSTORM_SID).first()


def get_users_by_seller(seller_sid: str) -> list[SellerUser]:
    return (
        session.query(SellerUser)
        .filter(SellerUser.seller_sid == seller_sid)
        .all()
    )


def get_user_by_tg_chat_id(tg_chat_id: int) -> SellerUser:
    return session.query(SellerUser).filter(SellerUser.tg_chat_id == tg_chat_id).first()

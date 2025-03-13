from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, session


class Seller(Base):
    __tablename__ = 'sellers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    token: Mapped[str] = mapped_column(nullable=True)
    sid: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    trade_mark: Mapped[str] = mapped_column(nullable=True)

    google_drive_folder_id: Mapped[str] = mapped_column(nullable=True)
    google_drive_stat_spreadsheet_id: Mapped[str] = mapped_column(nullable=True)
    google_drive_remains_spreadsheet_id: Mapped[str] = mapped_column(nullable=True)


def update_seller_data(token: str, sid: str, name: str, trade_mark: str, google_drive_folder_id, google_drive_spreadsheet_id, google_drive_remains_spreadsheet_id):
    session.query(Seller).filter_by(token=token).update(
        {
            'sid': sid, 
            'name': name, 
            'trade_mark': trade_mark, 
            'google_drive_folder_id': google_drive_folder_id, 
            'google_drive_stat_spreadsheet_id': google_drive_spreadsheet_id,
            'google_drive_remains_spreadsheet_id': google_drive_remains_spreadsheet_id
        }
    )
    session.commit()


def get_seller(id: int)  -> Seller:
    return session.query(Seller).filter_by(id=id).first()


def get_sellers_without_sid() -> list[Seller]:
    return session.query(Seller).filter_by(sid=None).all()


def get_sellers() -> list[Seller]:
    return session.query(Seller).filter(Seller.sid != None).all()

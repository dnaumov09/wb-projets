from db.model import Base, engine

import db.card
import db.order
import db.sale
import db.card_stat
import db.user
import db.settings


Base.metadata.create_all(bind=engine)

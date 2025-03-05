from db.model import Base, engine

import db.card
import db.order
import db.sale
import db.card_stat
import db.user
import db.settings
import db.warehouse
import db.remains
import db.warehouse_remains


Base.metadata.create_all(bind=engine)

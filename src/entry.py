from app import db

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    currency_id = db.Column(db.String, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Entry currency_id={self.currency_id} for_date={self.date}>"

def create_if_not_exists(entry: Entry):
    exists = db.session.query(Entry.id)\
                .filter_by(date=entry.date, currency_id=entry.currency_id)\
                .scalar() is not None
    if not exists:
         db.session.add(entry)

db.create_all()

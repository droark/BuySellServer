from webFiles import db, app
import sys

# The buy model.
class buyDB(db.Model):
    # ID will be ignored.
    id  = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer, index=True, unique=False)
    prc = db.Column(db.Float, index=True, unique=False)

    # Describes how to print class objects.
    def __repr__(self):
        return '<Buy Qty - %r Prc - %r>' % (self.qty, self.prc)


# The sell model.
class sellDB(db.Model):
    # ID will be ignored.
    id  = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer, index=True, unique=False)
    prc = db.Column(db.Float, index=True, unique=False)

    # Describes how to print class objects.
    def __repr__(self):
        return '<Sell Qty - %r Prc - %r>' % (self.qty, self.prc)

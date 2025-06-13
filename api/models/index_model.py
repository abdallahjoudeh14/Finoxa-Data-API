from mongoengine import *
from datetime import datetime


class Index(Document):
    ticker = StringField(
        required=True,
        unique=True,
    )
    name = StringField(required=True)
    exchange_name = StringField(
        db_field="exchangeName",
        required=True,
    )
    exchange = StringField(required=True)
    locale = StringField(required=True)
    market = StringField(default="indices")
    currency = StringField()
    created_at = DateTimeField(
        db_field="createdAt",
        default=datetime.now,
    )
    updated_at = DateTimeField(
        db_field="updatedAt",
        default=datetime.now,
    )

    meta = {
        "collection": "indices",
        "indexes": ["ticker"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Index, self).save(*args, **kwargs)

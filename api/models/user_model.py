from mongoengine import *
from datetime import datetime


class User(Document):
    name = StringField(
        required=True,
        max_length=50,
    )
    email = EmailField()
    password = StringField(
        required=True,
        min_length=8,
    )
    api_key = StringField(
        db_field="apiKey",
        default="",
    )
    created_at = DateTimeField(
        db_field="createdAt",
        required=True,
        default=datetime.now,
    )
    updated_at = DateTimeField(
        db_field="updatedAt",
        required=True,
        default=datetime.now,
    )
    meta = {
        "collection": "users",
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(User, self).save(*args, **kwargs)

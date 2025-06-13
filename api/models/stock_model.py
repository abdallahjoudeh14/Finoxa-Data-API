from mongoengine import *
from datetime import datetime


class Exchange(EmbeddedDocument):
    name = StringField()
    symbol = StringField()


class Address(EmbeddedDocument):
    street = StringField()
    city = StringField()
    state = StringField()
    zip_code = StringField(
        db_field="zipCode",
    )


class CompanyOfficer(EmbeddedDocument):
    name = StringField()
    title = StringField()
    maxAge = IntField()
    yearBorn = IntField()
    fiscalYear = IntField()
    exercisedValue = IntField()
    unexercisedValue = IntField()
    age = IntField()
    totalPay = IntField()


class Stock(Document):
    ticker = StringField(
        required=True,
        unique=True,
    )
    company_name = StringField(
        db_field="companyName",
        required=True,
    )
    description = StringField()
    sector = StringField()
    industry = StringField()
    exchange = EmbeddedDocumentField(Exchange)
    logo_url = StringField(
        db_field="logoUrl",
    )
    website = StringField()
    locale = StringField()
    country = StringField()
    address = EmbeddedDocumentField(Address)
    market = StringField(
        default="stocks",
    )
    phone = StringField()
    employees = IntField()
    company_officers = EmbeddedDocumentListField(
        CompanyOfficer,
        db_field="companyOfficers",
    )
    currency = StringField()
    market_cap = IntField(
        db_field="marketCap",
    )
    created_at = DateTimeField(
        default=datetime.now,
        db_field="createdAt",
    )
    updated_at = DateTimeField(
        default=datetime.now,
        db_field="updatedAt",
    )

    meta = {
        "collection": "stocks",
        "indexes": ["ticker"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Stock, self).save(*args, **kwargs)

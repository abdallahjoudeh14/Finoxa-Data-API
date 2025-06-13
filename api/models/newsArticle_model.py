from mongoengine import *
from datetime import datetime


class Publisher(EmbeddedDocument):
    name = StringField(required=True)
    homepage_url = StringField(
        db_field="homepageUrl",
        required=True,
    )
    logo_url = StringField(
        db_field="logoUrl",
        required=True,
    )


class Insight(EmbeddedDocument):
    ticker = StringField(required=True)
    sentiment = StringField(required=True)
    sentiment_reasoning = StringField(
        db_field="sentimentReasoning",
        required=True,
    )
    sentiment_score = FloatField(
        db_field="sentimentScore",
        required=True,
    )


class NewsArticle(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    article_url = StringField(
        db_field="articleUrl",
        required=True,
    )
    image_url = StringField(
        db_field="imageUrl",
        required=True,
    )
    authors = ListField(StringField())
    published_at = DateTimeField(
        db_field="publishedAt",
        required=True,
    )
    publisher = EmbeddedDocumentField(Publisher)
    tickers = ListField(StringField())
    insights = EmbeddedDocumentListField(Insight)
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
        "collection": "news_articles",
        "indexes": [
            {
                "fields": ["$title"],
                "default_language": "english",
                "weights": {
                    "company_name": 100,
                },
            },
        ],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(NewsArticle, self).save(*args, **kwargs)

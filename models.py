
from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, connect





class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()


meta = {"collection": "authors"}


class Quote(Document):
    author = ReferenceField(Author, required=True)
    quote = StringField(required=True)
    tags = ListField(StringField())


meta = {"collection": "quotes"}

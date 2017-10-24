from mongoengine import *
import datetime


class Page(Document):
    title = StringField(required=True)
    date_modified = DateTimeField(default=datetime.datetime.now)
    date_create = DateTimeField(default=datetime.datetime.now)
    task_id = ListField(required=True)
    text = StringField(required=True)
    url = StringField(required=True)
    search_query = StringField(required=True)
    snippet_number = IntField(required=True)
    uniq_id = StringField(required=True)

from sqlalchemy import Table, Column, Integer, ForeignKey
from models.base import Base

entry_topics = Table(
    'entry_topics', Base.metadata,
    Column('entry_id', Integer, ForeignKey('entries.id')),
    Column('topic_id', Integer, ForeignKey('topics.id'))
)

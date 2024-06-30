from sqlalchemy import DateTime, func, Column
from sqlalchemy.ext.declarative import declared_attr


class HelperModelMixin:
    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now())

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), onupdate=func.now())

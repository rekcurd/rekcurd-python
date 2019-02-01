from sqlalchemy import (
    Column, String, Boolean, UniqueConstraint
)

from .dao import db


class ModelAssignment(db.ModelBase):
    __tablename__ = 'model_assignments'
    __table_args__ = (
        UniqueConstraint('service_name'),
        {'mysql_engine': 'InnoDB'}
    )

    service_name = Column(String(512), primary_key=True)
    model_path = Column(String(512), nullable=False)
    first_boot = Column(Boolean(), nullable=False)

    @property
    def serialize(self):
        return {
            'service_name': self.service_name,
            'model_path': self.model_path,
            'first_boot': self.first_boot
        }

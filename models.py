"""furryCompanions Models."""
from sqlalchemy import Column, DateTime, Integer, String, func

from app import db


class Dogs(db.Model):
    """Represents the Dog table."""

    __tablename__ = 'dogs'

    id = Column('dog_id', Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    breed = Column(String(100), default='Unknown', nullable=False)
    fur_color = Column(String(50), default='', nullable=False)
    gender = Column(String(8), default='', nullable=False)
    age = Column(Integer, default=None)
    height = Column(Integer, default=None)
    length = Column(Integer, default=None)
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(DateTime, default=func.now(), server_onupdate=func.now())

    def __repr__(self):
        return '<Dog:{name}, {breed}>'.format(
            name=self.name,
            breed=self.breed,
        )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def dict_repr(self):
        return {
            'id': self.id,
            'name': self.name,
            'breed': self.breed,
            'fur_color': self.fur_color,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'length': self.length,
            'created_on': self.created_on.isoformat(),
            'updated_on': self.updated_on.isoformat(),
        }

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


# A Scientist has (visits) many Planets through Missions
# An Planet has (is visited by) many Scientists through Missions
# A Mission belongs to a Scientist and belongs to a Planet


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    serialize_only = ('id', 'name', 'distance_from_earth', 'nearest_star')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Relationship to missions
    missions = db.relationship("Mission", back_populates="planet")

    # Association proxy to scientists through missions
    scientists = association_proxy('missions', 'scientist')


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    serialize_only = ('id', 'name', 'field_of_study', 'missions')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Relationship to missions
    missions = db.relationship('Mission', back_populates='scientist')

    # Association proxy to planets through missions
    planets = association_proxy('missions', 'planet')

    @validates('name', 'field_of_study')
    def validate_name_and_study(self, key, value):
        if key == 'name':
            if not value:
                raise ValueError('Name cannot be empty.')
            
        elif key == 'field_of_study':
            if not value:
                raise ValueError('Field of study cannot be empty.')
            
        return value


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    serialize_only = ('id', 'name', 'planet')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Foreign keys
    scientist_id = db.Column(db.Integer, db.ForeignKey(
        'scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey(
        'planets.id'), nullable=False)

    # Relationships
    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')


    # Add validation
    @validates('name', 'scientist_id', 'planet_id')
    def validate_columns(self, key, value):
        if key == 'name':
            if not value:
                raise ValueError('Name cannot be empty.')
            
        elif key == 'scientist_id':
            if not value:
                raise ValueError('Scientist ID cannot be empty.')
            
        elif key == 'planet_id':
            if not value:
                raise ValueError('Planet ID cannot be empty.')
            
        return value

# add any models you may need.

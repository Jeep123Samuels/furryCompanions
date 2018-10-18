
from ast import literal_eval

from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from app import db, memcache_client
from models import Dogs
from webargs import fields, validate
from webargs.flaskparser import use_args

ALL_DOGS = 'all_dogs'

request_args = {
    'name': fields.Str(required=True),
    'fur_color': fields.Str(required=False),
    'breed': fields.Str(required=False),
    'gender': fields.Str(
        required=False,
        validate=validate.OneOf(['male', 'female']),
    ),
    'age': fields.Int(
        required=False,
        validate=validate.Range(min=0),
    ),
    'length': fields.Int(
        required=False,
        validate=validate.Range(min=0),
    ),
    'height': fields.Int(
        required=False,
        validate=validate.Range(min=0),
    ),
}


class CreateListDog(Resource):
    """Resource serving POST and GET-LIST requests."""
    args = request_args

    def get(self):
        # Return memcache instead.
        if memcache_client.get(ALL_DOGS):
            return literal_eval(memcache_client.get(ALL_DOGS).decode('utf8')), 200
        # Get all dogs from database.
        all_dogs = [
            dog.dict_repr()
            for dog in Dogs.query.all()
        ]
        # Store in memcache
        memcache_client.set(ALL_DOGS, all_dogs, expire=60)
        return all_dogs, 200

    @use_args(args)
    def post(self, args):
        try:
            name = args.get('name')
            dog = Dogs(name=name)
            for key, value in args.items():
                setattr(dog, key, value)
            dog.save()
            # Remove all_dogs memcache as it's stale.
            memcache_client.delete(ALL_DOGS)
            return dog.dict_repr(), 201

        except SQLAlchemyError as exception_message:
            db.session.rollback()
            return {'error': str(exception_message)}, 403


class UpdateDog(Resource):
    """Resource serving PUT requests."""

    args = {
        'id': fields.Int(
            required=True,
            validate=validate.Range(min=1),
        ),

    }
    args.update(request_args)

    @use_args(args)
    def put(self, args):
        dog_id = args.get('id')
        dog = Dogs.query.filter_by(id=dog_id).first()
        if not dog:
            return {'error': 'Dog could not be found.'}, 404
        try:
            for key, value in args.items():
                setattr(dog, key, value)
            dog.save()
            # Delete all_dogs memcache as it is stale
            memcache_client.delete(ALL_DOGS)
            # update memcache with obj id.
            memcache_client.set(str(dog_id), dog.dict_repr(), expire=60)
            return dog.dict_repr(), 200

        except SQLAlchemyError as exception_message:
            db.session.rollback()
            return {'error': str(exception_message)}, 403


class DeleteGetDog(Resource):
    """Resource serving GET and DELETE requests."""
    args = request_args

    def get(self, dog_id):
        # Check if memcache have the data.
        if not memcache_client.get(str(dog_id)):
            dog = Dogs.query.filter_by(id=dog_id).first()
            if not dog:
                return {'error': 'Dog could not be found.'}, 404
            # Set object into memcache.
            memcache_client.set(str(dog_id), dog.dict_repr(), expire=60)

        # Always return the memcache data.
        memcache_data = memcache_client.get(str(dog_id))
        return literal_eval(memcache_data.decode('utf-8')), 200

    def delete(self, dog_id):
        dog = Dogs.query.filter_by(id=dog_id).first()
        if not dog:
            return {'error': 'Dog could not be found.'}, 404
        try:
            dog.delete()
            # Delete all_dogs and the single obj from memcache.
            memcache_client.delete(str(dog_id))
            memcache_client.delete(ALL_DOGS)
            return 'Deleted Successfully', 200

        except SQLAlchemyError as exception_message:
            db.session.rollback()
            return {'error': str(exception_message)}, 403

#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os
import pprint

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''


class ScientistResource(Resource):
    def get(self):
        try:
            scientists = Scientist.query.all()
            response_body = [scientist.to_dict(
                only=('id', 'name', 'field_of_study')) for scientist in scientists]
            return make_response(response_body, 200)
        except:
            return {}, 500

    # post request handler ; create new scientist with name and field of study

    def post(self):
        name = request.json.get('name')
        field_of_study = request.json.get('field_of_study')
        if not name or not field_of_study:
            return {
                "errors": ["validation errors"]
            }, 400

        scientist = Scientist(name=name, field_of_study=field_of_study)
        db.session.add(scientist)
        db.session.commit()

        return make_response(scientist.to_dict(only=('id', 'name', 'field_of_study')), 201)


api.add_resource(ScientistResource, '/scientists')


class ScientistByID(Resource):
    def get(self, id):
        try:
            scientist = Scientist.query.filter_by(id=id).first()
            if scientist:
                response_body = scientist.to_dict(
                    only=('id', 'name', 'missions', 'field_of_study'))
                # breakpoint()
                return make_response(response_body, 200)
            else:
                return make_response(jsonify({'error': 'Scientist not found'}), 404)
        except:
            return {}, 500

    # delete request handler; return 404 if activity does not exists.

    def delete(self, id):
        # query the scientist by id
        scientist = Scientist.query.filter_by(id=id).first()

        if scientist:
            # delete associated missions
            for mission in scientist.missions:
                db.session.delete(mission)
            # delete scientist
            db.session.delete(scientist)
            db.session.commit()
            return make_response({"message": "Scientist successfully deleted."}, 204)
        else:
            return {"error": "Scientist not found"}, 404

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404

        data = request.json
        name = data.get('name')
        field_of_study = data.get('field_of_study')

   # Validate fields
        if name is not None and not isinstance(name, str):
            return {
                "errors": ["validation errors"]
            }, 400
        if name == '':
            return {
                "errors": ["validation errors"]
            }, 400
        if field_of_study is not None and not isinstance(field_of_study, str):
            return {
                "errors": ["validation errors"]
            }, 400
        if field_of_study == '':
            return {
                "errors": ["validation errors"]
            }, 400

        # Update fields
        if name is not None:
            scientist.name = name
        if field_of_study is not None:
            scientist.field_of_study = field_of_study

        db.session.add(scientist)
        db.session.commit()

        return make_response(scientist.to_dict(only=('id', 'name', 'field_of_study')), 202)


api.add_resource(ScientistByID, '/scientists/<int:id>')


class Planets(Resource):
    def get(self):
        try:
            planets = Planet.query.all()
            response_body = [planet.to_dict() for planet in planets]
            return make_response(response_body, 200)
        except:
            return {}, 500


api.add_resource(Planets, '/planets')


class Missions(Resource):
    def post(self):
        # creates a new mission : name, foreign keys
        try:
            name = request.json.get('name')
            planet_id = request.json.get('planet_id')
            scientist_id = request.json.get('scientist_id')

            # validations
            if not name:
                return {
                    "errors": ["validation errors"]
                }, 400
            if not planet_id or not scientist_id:
                return {
                    "errors": ["validation errors"]
                }, 400

            new_mission = Mission(
                name=name,
                planet_id=planet_id,
                scientist_id=scientist_id
            )

            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(only=('id', 'name', 'planet', 'scientist_id', 'planet_id', 'scientist')), 201)
        except:
            return {
                "errors": ["validation errors"]
            }, 404


api.add_resource(Missions, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

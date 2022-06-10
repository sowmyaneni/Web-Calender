from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse, inputs
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import sys, datetime
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# write your code here

parser = reqparse.RequestParser()
parser.add_argument(
    'event',
    type=str,
    help='The event name is required!',
    required=True
)
parser.add_argument(
    'date',
    type=inputs.date,
    help='The event date with the correct format is required! The correct format is YYYY-MM-DD!',
    required=True
)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


class EventsSchema(Schema):
    id = fields.Integer()
    event = fields.String()
    date = fields.Date('%Y-%m-%d')


event_schema = EventsSchema()
events_schema = EventsSchema(many=True)

class EventsResource(Resource):
   
    def get(self):
        if request.args:
            args = request.args
            start_time = args['start_time']
            end_time = args['end_time']
            event = Events.query.filter(Events.date.between(start_time, end_time)).all()
            return events_schema.dump(event)
        else:
            events = Events.query.all()
            return events_schema.dump(events)

    def post(self):
        args = parser.parse_args()
        new_event = Events(
            event=args['event'],
            date=args['date'].date()
        )
        db.session.add(new_event)
        db.session.commit()
        return {
            'message': 'The event has been added!',
            'event': args['event'],
            'date': str(args['date'].date())
        }


class EventResource(Resource):
    def get(self):
        event = Events.query.filter(Events.date == datetime.date.today()).all()
        return events_schema.dump(event)


class EventsByID(Resource):
    def get(self, id):
        event = Events.query.filter(Events.id == id).first()
        print(event)
        if not event:
            abort(404, "The event doesn't exist!")
        return event_schema.dump(event)

    def delete(self, id):
        event = Events.query.filter(Events.id == id).first()
        if not event:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(event)
            db.session.commit()
            return {"message": "The event has been deleted!"}, 200



api.add_resource(EventsResource, '/event')
api.add_resource(EventResource, '/event/today')
api.add_resource(EventsByID, '/event/<int:id>')



# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(debug=True)

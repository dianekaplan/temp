import time
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)


class Tube(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String, unique=True, nullable=False)
    status = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)


class TubeSchema(ma.Schema):
    class Meta:
        fields = ("id", "barcode", "status", "user_id")
        model = Tube


tube_schema = TubeSchema()
tubes_schema = TubeSchema(many=True)


class TubeProcessingResource(Resource):

    # Get all tubes with 'registered' status
    def get(self):
        registered_tubes = Tube.query.filter_by(status="registered").all()
        return tubes_schema.dump(registered_tubes)

    # Create a new tube with unique barcode (using epoch seconds) and return the barcode
    def post(self):
        new_tube = Tube(
            barcode=int(time.time()),
            status='new',
            user_id=0,
        )
        db.session.add(new_tube)
        db.session.commit()
        return new_tube.barcode

    # Bulk update the status for given tubes (by barcode)
    # expected request body format: [{"barcode": "1234", "status": "positive"},{"barcode": "5678", "status": "negative"}]
    def patch(self):
        lines_to_update = request.json['body']
        tubes_updated = 0
        barcodes_not_found = []
        lines_missing_barcode_or_status = []

        # handle invalid format (missing barcode or status) otherwise update the tube
        for line in lines_to_update:
            try:
                line['status'] and line['barcode']
            except:
                lines_missing_barcode_or_status.append(line)

            else:
                tube_found = Tube.query.filter_by(barcode=line['barcode']).first()

                if tube_found:
                    tube_found.status = line['status']
                    tubes_updated += 1
                else:
                    barcodes_not_found.append(line['barcode'])

        db.session.commit()
        return f"{tubes_updated} tubes updated, {len(barcodes_not_found)} barcodes not found: {barcodes_not_found}, " \
               f" {len(lines_missing_barcode_or_status)} invalid lines (missing barcode or status): " \
               f"{lines_missing_barcode_or_status}."


api.add_resource(TubeProcessingResource, '/tubes')


@app.route("/")
def hello_world():
    return {"hello": "world"}

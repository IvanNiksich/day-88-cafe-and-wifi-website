from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

API_KEY = "TopSecretAPIKey"

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# Route to get a random cafe
@app.route('/choice_random', methods=['GET'])
def choice_random():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    if not all_cafes:
        return jsonify({'message': 'No cafes found'}), 404
    selected_cafe = random.choice(all_cafes)
    # return jsonify({'id': selected_cafe.id,
    #                 'name': selected_cafe.name,
    #                 "map_url": selected_cafe.map_url,
    #                 "img_url": selected_cafe.img_url,
    #                 "location": selected_cafe.location,
    #                 "seats": selected_cafe.seats,
    #                 "has_toilet": selected_cafe.has_toilet,
    #                 "has_wifi": selected_cafe.has_wifi,
    #                 "has_sockets": selected_cafe.has_sockets,
    #                 "can_take_calls": selected_cafe.can_take_calls,
    #                 "coffee_price": selected_cafe.coffee_price
    #                 })
    return jsonify(selected_cafe.as_dict())


@app.route('/all_cafes_data', methods=['GET'])
def all_cafes_data():
    with app.app_context():
        all_cafes = Cafe.query.all()
        if not all_cafes:
            return jsonify({'message': 'No cafes found'}), 404
        result = []
        for cafe in all_cafes:
            result.append(cafe.as_dict())
        return jsonify(result)


@app.route('/search', methods=['GET'])
def search():
    loc = request.args.get("loc")
    with app.app_context():
        cafes_search = Cafe.query.filter_by(location=loc).all()
        if not cafes_search:
            return jsonify(error={'Not Found': "Sorry we don't have a cafe at that location"}), 404
        result = []
        for cafe in cafes_search:
            result.append(cafe.as_dict())
        return jsonify(result)


@app.route('/add', methods=['GET', 'POST'])
def add():
    name = request.form.get("name")
    map_url = request.form.get("map_url")
    img_url = request.form.get("img_url")
    location = request.form.get("location")
    seats = request.form.get("seats")
    has_toilet = bool(request.form.get("has_toilet"))
    has_wifi = bool(request.form.get("has_wifi"))
    has_sockets = bool(request.form.get("has_sockets"))
    can_take_calls = bool(request.form.get("can_take_calls"))
    coffee_price = request.form.get("coffee_price")
    print(name)
    print(map_url)
    with app.app_context():
        new_cafe = Cafe(name=name,
                        map_url=map_url,
                        img_url=img_url,
                        location=location,
                        seats=seats,
                        has_toilet=has_toilet,
                        has_wifi=has_wifi,
                        has_sockets=has_sockets,
                        can_take_calls=can_take_calls,
                        coffee_price=coffee_price
                        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={'Success': "Successfully added  the new cafe."})


@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    with app.app_context():
        cafe_edit = Cafe.query.filter_by(id=cafe_id).first()
        if not cafe_edit:
            return jsonify(error={'Not Found': "Sorry a cafe with that id was not found in the database"}), 404
        print(cafe_edit.coffee_price)
        print(new_price)
        cafe_edit.coffee_price = new_price
        db.session.commit()
        return jsonify(response={'Success': "Successfully updated the price."})


@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def report_closed(cafe_id):
    api_key = request.args.get("api-key")
    print(api_key)
    with app.app_context():
        if api_key == "TopSecretAPIKey":
            cafe_delete = Cafe.query.filter_by(id=cafe_id).first()
            if not cafe_delete:
                return jsonify(error={'Not Found': "Sorry a cafe with that id was not found in the database"}), 404

            db.session.delete(cafe_delete)
            db.session.commit()
            return jsonify(response={'Success': "Successfully deleted the cafe."})

        return jsonify(error={'Forbidden': "Sorry that's not allowed. Make sure you have the correct api_key."}), 402


# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_bootstrap import Bootstrap5


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
app.secret_key = API_KEY

bootstrap = Bootstrap5(app)


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


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    location = StringField("Cafe's neighborhood", validators=[DataRequired()])
    coffee_price = StringField("Coffee's price?", validators=[DataRequired()])
    has_wifi = SelectField(
        "Is there Wifi for clients?",
        choices=[
            ('1', 'Yes'),
            ('0', 'No'),
        ],
        validators=[DataRequired()]
    )
    has_sockets = SelectField(
        "Are there sockets available for clients?",
        choices=[
            ('1', 'Yes'),
            ('0', 'No'),
        ],
        validators=[DataRequired()]
    )
    can_take_calls = SelectField(
        "Is it a good place to take calls?",
        choices=[
            ('1', 'Yes'),
            ('0', 'No'),
        ],
        validators=[DataRequired()]
    )
    seats = SelectField(
        "Number of seats",
        choices=[
            ('0-10', '0-10'),
            ('10-20', '10-20'),
            ('20-30', '20-30'),
            ('30-40', '30-40'),
            ('50+', '50+'),
        ],
        validators=[DataRequired()]
    )
    has_toilet = SelectField(
        "Does it have toilets available?",
        choices=[
            ('1', 'Yes'),
            ('0', 'No'),
        ],
        validators=[DataRequired()]
    )
    map_url = StringField("Map location's url", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe's image url", validators=[DataRequired(), URL()])
    submit = SubmitField(label="Add cafe")


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    my_cafes = all_cafes_data()
    cafes = my_cafes.json
    return render_template("index.html", cafes=cafes)


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


# HTTP GET - Read All Records
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


# HTTP GET - Search by location
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


# HTTP POST - Create Record
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = CafeForm()
    if form.validate_on_submit():
        with app.app_context():
            new_cafe = CafeForm(name=form.name.data,
                                map_url=form.map_url.data,
                                img_url=form.img_url.data,
                                location=form.location.data,
                                seats=form.seats.data,
                                has_toilet=bool(form.has_toilet.data),
                                has_wifi=bool(form.has_wifi.data),
                                has_sockets=bool(form.has_sockets.data),
                                can_take_calls=bool(form.can_take_calls.data),
                                coffee_price=form.coffee_price.data,
                                )
            print(new_cafe)
            # db.session.add(new_cafe)
            # db.session.commit()
            # return jsonify(response={'Success': "Successfully added  the new cafe."})
            return redirect(url_for("home"))

    return render_template("add.html", form=form)


# HTTP PUT/PATCH - Update Record
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


# HTTP DELETE - Delete Record
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


if __name__ == '__main__':
    app.run(debug=True)

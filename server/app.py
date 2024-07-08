#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def home():
    return "<h1>Welcome to the Pizza Restaurant API</h1>"

class ListRestaurants(Resource):
    def get(self):
        all_restaurants = Restaurant.query.all()
        return make_response(jsonify([restaurant.to_dict() for restaurant in all_restaurants]), 200)

class SingleRestaurant(Resource):
    def get(self, restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if restaurant:
            return make_response(jsonify(restaurant.to_dict()), 200)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    def delete(self, restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

class ListPizzas(Resource):
    def get(self):
        all_pizzas = Pizza.query.all()
        return make_response(jsonify([pizza.to_dict() for pizza in all_pizzas]), 200)

class ListRestaurantPizzas(Resource):
    def get(self):
        all_restaurant_pizzas = RestaurantPizza.query.all()
        return make_response(jsonify([rp.to_dict() for rp in all_restaurant_pizzas]), 200)
    
    def post(self):
        data = request.get_json()
        restaurant_id = data.get("restaurant_id")
        pizza_id = data.get("pizza_id")
        price = data.get("price")
        
        if not restaurant_id or not pizza_id or not price:
            return make_response(jsonify({"errors": ["Missing required fields"]}), 400)
        
        restaurant = Restaurant.query.get(restaurant_id)
        pizza = Pizza.query.get(pizza_id)
        
        if not restaurant or not pizza:
            return make_response(jsonify({"errors": ["Restaurant or Pizza not found"]}), 404)
        
        try:
            new_restaurant_pizza = RestaurantPizza(restaurant_id=restaurant_id, pizza_id=pizza_id, price=price)
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        except ValueError as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)

api.add_resource(ListRestaurants, '/restaurants')
api.add_resource(SingleRestaurant, '/restaurants/<int:restaurant_id>')
api.add_resource(ListPizzas, '/pizzas')
api.add_resource(ListRestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)

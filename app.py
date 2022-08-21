import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# config database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# migrate db
migrate = Migrate(app, db)


# create table
class Recipe(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return self.name

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, pk):
        return cls.query.get_or_404(pk)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# create serializer
class RecipeSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()


@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    recipe = Recipe.get_all()
    serializer = RecipeSchema(many=True)
    data = serializer.dump(recipe)
    return jsonify(data)


@app.route('/recipes', methods=['POST'])
def create_new_recipe():
    name = request.form.get('name')
    description = request.form.get('description')

    new_recipe = Recipe(
        name=name,
        description=description
    )
    new_recipe.save()

    serializer = RecipeSchema()
    data = serializer.dump(new_recipe)

    return jsonify(data), 201


@app.route('/recipes/<int:pk>', methods=['GET'])
def get_recipe(pk):
    recipe = Recipe.get_by_id(pk)
    serializer = RecipeSchema()
    data = serializer.dump(recipe)

    return jsonify(data)


@app.route('/recipes/<int:pk>', methods=['PUT'])
def update_recipe(pk):
    recipe = Recipe.get_by_id(pk)
    name = request.form.get('name')
    description = request.form.get('description')

    recipe.name = name
    recipe.description = description

    db.session.commit()

    serializer = RecipeSchema()
    data = serializer.dump(recipe)

    return jsonify(data)


@app.route('/recipes/<int:pk>', methods=['DELETE'])
def delete_recipe(pk):
    recipe = Recipe.get_by_id(pk)
    recipe.delete()

    return jsonify({'message': 'Deleted'}), 204


@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404


@app.errorhandler(500)
def internal_server(error):
    return jsonify({"message": "There is a problem"}), 500


if __name__ == '__main__':
    app.run(debug=True)

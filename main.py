from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    second_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"User: {self.first_name} {self.second_name}"

userFields = {
    "id": fields.Integer,
    "first_name": fields.String,
    "second_name": fields.String,
    "email": fields.String,
    "birthdate": fields.String
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFields)
    def post(self):
        user_args = reqparse.RequestParser()
        user_args.add_argument("first_name", 
                               type=str, 
                               required=True, 
                               help="first name field cannot be blank")
        user_args.add_argument("second_name", 
                               type=str, 
                               required=True, 
                               help="second name field cannot be blank")
        user_args.add_argument("email", 
                               type=str, 
                               required=True, 
                               help="email field cannot be blank")
        user_args.add_argument("birthdate",
                               type=str, 
                               required=True, 
                               help="birthdate field cannot be blank")
        args = user_args.parse_args()
        user = UserModel(first_name=args.get("first_name"),
                         second_name=args.get("second_name"),
                         email=args.get("email"),
                         birthdate=datetime.strptime(args.get("birthdate"), "%Y-%m-%d"))
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users


class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user

    @marshal_with(userFields)
    def patch(self, id):
        user_args = reqparse.RequestParser()
        
        user_args.add_argument("first_name", 
                               type=str, 
                               required=False)
        user_args.add_argument("second_name", 
                               type=str, 
                               required=False)
        user_args.add_argument("email", 
                               type=str, 
                               required=False)
        user_args.add_argument("birthdate",
                               type=str, 
                               required=False)        
        args = user_args.parse_args()
        print(args)
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        user.first_name=args.get("first_name")
        user.second_name=args.get("second_name")
        user.email=args.get("email")
        if args.get("birthdate"):
            user.birthdate=datetime.strptime(args["birthdate"], "%Y-%m-%d")
        db.session.commit()
        return user    

    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)    
        db.session.commit()
        users = UserModel.query.all()
        return users


api.add_resource(Users, "/api/users")
api.add_resource(User, "/api/users/<int:id>")


if __name__ == "__main__":
    app.run(debug=True)

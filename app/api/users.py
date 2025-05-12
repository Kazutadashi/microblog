from app.api import bp
from app.models import User
from app import db
import sqlalchemy as sa
from flask import request

@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return db.get_or_404(User, id).to_dict()

@bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(sa.select(User), page, per_page, 'api.get_users')

@bp.route('/users/<int:id>/followers', methods=['GET'])
def get_followers(id):
    user = db.get_or_404(User, id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(user.followers.select(), page, 'api.get_followers', id=id)


@bp.route('/users/<int:id>/following', methods=['GET'])
def get_following(id):
    user = db.get_or_404(User, id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(user.following.select(), page, per_page, 'api.get_following', id=id)

@bp.route('/users', methods=['POST'])
def create_user():
    pass

@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass



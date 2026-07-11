"""
routes/watchlist.py — CineLog (feature/watchlist branch)

Endpoints for the watchlist feature.
"""

from flask import Blueprint, jsonify, request
from services.watchlist_service import add_to_watchlist, get_watchlist, remove_from_watchlist, handle_watchlist_publicity
from services.collection_service import FilmNotFoundError
from models import WatchlistEntry

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/<user_id>", methods=["GET"])
def view_watchlist(user_id):
    """GET /watchlist/<user_id> — Return the user's watchlist."""
    films = get_watchlist(user_id)
    return jsonify(films)


@watchlist_bp.route("/<user_id>/add", methods=["POST"])
def add_film(user_id):
    """
    POST /watchlist/<user_id>/add

    Body: { 
    "film_id": <int>,
    "public": bool
        }
    """
    data = request.get_json()
    if not data or "film_id" not in data or "public" not in data:
        return jsonify({"error": "film_id and publicity choice are required"}), 400

    entry = add_to_watchlist(user_id=user_id, film_id=data["film_id"], public=data["public"])
    return jsonify(entry.to_dict()), 201


@watchlist_bp.route("/<user_id>/remove", methods=["DELETE"])
def remove_film(user_id):
    """
    DELETE /watchlist/<user_id>/remove

    Body: { "film_id": <uuid> }
    """
    data = request.get_json()
    if not data or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400
    film_id = data['film_id']
    remove_from_watchlist(user_id=user_id, film_id=film_id)
    return jsonify({"message": f"'{film_id}' removed from users watchlist"}), 200


@watchlist_bp.route("/<user_id>/publicity", methods=["PATCH"])
def update_watchlist_publicity(user_id):
    """
    PATCH /watchlist/<user_id>/publicity

    Body: { 
    
    "watchlist_id": <uuid>,    
    "public": bool
    
    }
    """
    data = request.get_json()
    if not data or "watchlist_id" not in data or "public" not in data:
        return jsonify({"error": "watchlist_id is required"}), 400
    
    watchlist_id = data['watchlist_id']
    choice = data['public']
    handle_watchlist_publicity(user_id=user_id, watchlist_id=watchlist_id, public=choice)
    return jsonify({"message": f"'{watchlist_id}' set to {choice}"}), 200

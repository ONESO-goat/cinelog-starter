"""
services/watchlist_service.py — CineLog (feature/watchlist branch)

Business logic for the watchlist feature.
"""

from app import db
from models import Film, WatchlistEntry
from services.collection_service import FilmNotFoundError

class WatchlistDoesntExistError(Exception):
    pass

class AlreadyInWatchlistError(Exception):
    """Raised when a film is already in the user's watchlist."""
    pass

class FilmNotInWatchlistError(Exception):
    """Raised when a film is not inside the user's watchlist."""
    pass

def add_to_watchlist(user_id, film_id, public:bool=True):
    """
    Add a film to a user's watchlist.

    Args:
        user_id (str): UUID of the user.
        film_id (int): ID of the film. (Note: integer — pre-refactor)
        public (bool): Make the watchlist public (True) or private (False)

    Returns:
        WatchlistEntry: The newly created entry.

    Raises:
        FilmNotFoundError: If film_id does not exist.
    """
    film = db.session.get(Film, film_id)
    if film is None:
        raise FilmNotFoundError(f"No film found with id '{film_id}'")

    existing = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    
    if existing:
        raise AlreadyInWatchlistError(
            f"Film '{film_id}' is already in this user's watchlist"
        )
        
    entry = WatchlistEntry(user_id=user_id, film_id=film_id, public=public)

    db.session.add(entry)
    db.session.commit()
    return entry


def get_watchlist(user_id):
    """
    Return all films on a user's watchlist.

    Args:
        user_id (str): UUID of the user.

    Returns:
        list[dict]: List of film dicts with watchlist metadata attached.
    """
    entries = (
        WatchlistEntry.query
        .filter_by(user_id=user_id)
        .join(Film)
        .order_by(WatchlistEntry.date_added.desc())
        .all()
    )

    result = []
    for entry in entries:
        film_dict = entry.film.to_dict()
        film_dict["date_added"] = entry.date_added.isoformat()
        film_dict["public"] = entry.public
        result.append(film_dict)

    return result

def handle_watchlist_publicity(user_id, watchlist_id, public:bool)->bool:
    """
    Update the visibility status of a specific watchlist.

    Args:
        user_id (str/int): The ID of the user owning the watchlist.
        watchlist_id (str): The ID of the watchlist to update.
        public (bool): True to make public, False to make private.
    """
    if not watchlist_id or public is None:
        raise ValueError("watchlist id or publicity choice is required")
    
    entry = WatchlistEntry.query.filter_by(id=watchlist_id, user_id=user_id).first()
    if not entry:
        raise WatchlistDoesntExistError(f"'{watchlist_id}' doesnt exist for this user")

    entry.public = public
    
    db.session.commit()
    return entry.public
    
def remove_from_watchlist(user_id, film_id):
    """
    remove a film to a user's watchlist.

    Args:
        user_id (str): UUID of the user.
        film_id (str): The UUID of the film to remove.

    Raises:
        FilmNotFoundError: If film_id does not exist.
        FilmNotInWatchlistError: If the film is not in the user's watchlist.
    """
    
    film = db.session.get(Film, film_id)
    if film is None:
        raise FilmNotFoundError(f"No film found with id '{film_id}'")

    entry = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    
    if not entry:
        raise FilmNotInWatchlistError(
            f"Film '{film_id}' is not in the user's watchlist"
        )

    db.session.delete(entry)
    db.session.commit()



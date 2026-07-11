"""
tests/test_collection.py — CineLog

Tests for the collection service.
These tests demonstrate the patterns used across the codebase — read them
before writing your own tests for the watchlist feature (see Comment 4).
"""

import pytest
from app import create_app, db
from models import User, Film, CollectionEntry, WatchlistEntry
from services.collection_service import FilmNotFoundError
from services.watchlist_service import (
    AlreadyInWatchlistError,
    filmNotInWatchlistError,
    get_watchlist,
    add_to_watchlist, 
    handle_watchlist_publicity,
    remove_from_watchlist
)


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="spiderverse", year=2018, genre="action")
        db.session.add(film)
        db.session.commit()
        return film.id

@pytest.fixture
def sample_watchlist(app, sample_user, sample_film):
    """A film to use in tests."""

    with app.app_context():
        watchlist = WatchlistEntry(user_id=sample_user, film_id=sample_film)
        db.session.add(watchlist)
        db.session.commit()
        return watchlist.id


def test_film_is_inside_users_watchlist(app, sample_user, sample_film, sample_watchlist):
    with app.app_context():
        films = get_watchlist(user_id=sample_user)
        assert len(films) > 0
        movie_ids= [film['id'] for film in films]
        assert sample_film in movie_ids

def test_add_to_watchlist_nonexistent_film(app, sample_user, sample_film, sample_watchlist):
    """
        Adding a film_id that doesn't exist in the database should raise
        FilmNotFoundError, not a database integrity error.
    """
    fake_film_id = "00000000-0000-0000-0000-000000000000"
    with app.app_context():
        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)
        
    
def test_film_already_inside_watchlist(app, sample_user, sample_film, sample_watchlist):
    with app.app_context():
        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)
        
    
    
def test_add_film_to_watchlist(app, sample_user):
    with app.app_context():
        movie1 = Film(title="project x", year=2012, genre="comedy")
        movie2 = Film(title="chronicle", year=2012, genre="sci-fi")
        
        db.session.add_all([movie1, movie2])
        db.session.commit()
        
        add_to_watchlist(user_id=sample_user, film_id=movie1.id)
        add_to_watchlist(user_id=sample_user, film_id=movie2.id)
        films = get_watchlist(user_id=sample_user)
        movie_titles = [film['title'] for film in films]
        
        assert "chronicle" in movie_titles
        assert "project x" in movie_titles

def test_film_not_inside_watchlist(app, sample_user, sample_film, sample_watchlist):
    movie1 = Film(title="project x", year=2012, genre="comedy")

    db.session.add(movie1)
    db.session.commit()

    with app.app_context():
        with pytest.raises(filmNotInWatchlistError):
            remove_from_watchlist(user_id=sample_user, film_id=movie1.id)
        
    
def test_remove_film_to_watchlist(app, sample_user):
    with app.app_context():
        movie1 = Film(title="project x", year=2012, genre="comedy")
        movie2 = Film(title="chronicle", year=2012, genre="sci-fi")
        
        db.session.add_all([movie1, movie2])
        db.session.commit()
        
        add_to_watchlist(user_id=sample_user, film_id=movie1.id)
        add_to_watchlist(user_id=sample_user, film_id=movie2.id)
        films = get_watchlist(user_id=sample_user)
        movie_titles = [film['title'] for film in films]
        
        assert "chronicle" in movie_titles
        assert "project x" in movie_titles
        
        remove_from_watchlist(user_id=sample_user, film_id=movie1.id)
        remove_from_watchlist(user_id=sample_user, film_id=movie2.id)
        films = get_watchlist(user_id=sample_user)
        movie_titles = [film['title'] for film in films]
        
        assert "chronicle" not in movie_titles
        assert "project x" not in movie_titles
        
def test_handle_watchlist_publicity(app, sample_user, sample_film, sample_watchlist):
    """
    Toggle the publicity of a watchlist.
    """
    with app.app_context():
        handle_watchlist_publicity(user_id=sample_user, watchlist_id=sample_watchlist, public=False)
        assert WatchlistEntry.query.get(sample_watchlist).public is False# entry.public defaults to public
        handle_watchlist_publicity(user_id=sample_user, watchlist_id=sample_watchlist, public=True)
        assert WatchlistEntry.query.get(sample_watchlist).public is True
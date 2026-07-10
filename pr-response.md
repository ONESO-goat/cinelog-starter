# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename
**What I did:** 
    Changed the name of the function save_to_watchlist() -> add_to_watchlist() inside services/watchlist_service.py

**How I verified:**
    Checking that all calls of the function was add_to_watchlist() and not save_to_watchlist()

## Comment 2 — Deduplication
**What I did:**

added a unique limiter

```python

class Film(db.Model):
    ...
    watchlist_entries = db.relationship("WatchlistEntry", backref="film", lazy=True)

class WatchlistEntry(db.Model):
    ...
    __table_args__ = (
            db.UniqueConstraint("user_id", "film_id", name="unique_user_film_saved_to_watchlist"),
        )
```
to watchlist model so there can only be 1 instance of a user and a film.

Added the exception **AlreadyInWatchlistError**
```python
class AlreadyInWatchlistError(Exception):
    """Raised when a film is already in the user's watchlist."""
    pass
```

to handle already existing user and film watchlist instances. 

I addded code to the that checks if the user already has the flim listed inside a watchlist.
```python 
def add_to_watchlist(user_id, film_id):
    ...
    existing = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    
    if existing:
        raise AlreadyInWatchlistError(
            f"Film '{film_id}' is already in this user's watchlist"
        )
```

**How I verified:**

Added **test/test_watchlist** that deals with all watchlist services. The file test weather a film is inside the users watchlist, test if the AlreadyInWatchlistError works corrctly, and test if add_to_watchlist() works as expected

## Comment 3 — Missing test
**What I did:**
**How I verified:**

## Comment 4 — Default visibility
**My position:**
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->
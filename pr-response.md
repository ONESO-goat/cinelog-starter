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

Used test_film_already_inside_watchlist() inside test/test_watchtest.

## Comment 3 — Missing test
**What I did:**
Added **test/test_watchlist** that deals with all watchlist services. The file test weather a film is inside the users watchlist, test if the AlreadyInWatchlistError works corrctly, and test if add_to_watchlist() works as expected

**How I verified:**

Running the file for each test separately, making sure everything went smooth and works as expected.

## Comment 4 — Default visibility
**My position:** 
    **Agreed**

**Reasoning:** 
    Defaulting the watchlist to public seems to be well put and is the norm in the industery. Just make sure there's an option where the user can set it to private either during or after deployment. This choice helps with the social scene of the application.

**Tradeoff acknowledged:**

* A new user is lost on where or how to set the post to private 
* The user doesn't want to waste their time setting every new watchlist item to private manually
* The user forgot to set the watchlist to private during deployment
* Possible risk of other users interacting with the watchlist maliciously
* If the user has loads of films in their watchlist and want to put all to private. But this can be said vice versa

## Comment 5 — Sort order
**My position:**
    Go with **Date Added** (Agree with reviewer)

**Reasoning:**
   Defaulting to "Date Added" aligns with modern user experience in applications. Surfacing the most recent items reduces cognitive load, as users naturally expect to see their latest actions at the top of the list. A chronological view provides context regarding user engagement and momentum, making the application feel dynamic and personalized to their recent activity rather than stagnant.

**Engagement with reviewer's point:**
    I fully agree with the reviewer's recommendation to default to Date Added. Their point correctly identifies that a chronological sort order enhances usability by prioritizing top  of mind content. By implementing this, we ensure that users don't have to hunt for their newly created items, creating a much smoother onboarding and daily workflow.

## Comment 6 — Rebase
**What conflicted:**
    Inside WatchlistEntry, the film_id was an integer column rather than string.

**How I resolved it:**
    Just make it string that takes the length of an uuid.
    
**How I verified no conflict remains:**
    Continued the rebase where I faced no other conflict.

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->
# PR Response Document — CineLog Watchlist Feature

## AI Usage

I used AI (ChatGPT) for:

* Improving the structure
* Improving the grammar
* Ensuring the document followed the rubric and included all required context.

I did not use AI while writing or implementing the code.

---

# Comment 1 — Rename

### What I changed

Renamed the function `save_to_watchlist()` to `add_to_watchlist()` in `services/watchlist_service.py` to better reflect its purpose.

### How I verified it

I used my editor's project-wide search to locate every reference to `save_to_watchlist()` and updated each call site to `add_to_watchlist()`. This included the service implementation and any files that referenced the function. After the rename, I ran the test suite to confirm there were no remaining references to the old function name.


---

# Comment 2 — Deduplication

### What I changed

To prevent duplicate watchlist entries, I added a unique constraint to the `WatchlistEntry` model so that each user can only save a specific film once.

```python
class Film(db.Model):
    ...
    watchlist_entries = db.relationship("WatchlistEntry", backref="film", lazy=True)

class WatchlistEntry(db.Model):
    ...
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "film_id",
            name="unique_user_film_saved_to_watchlist",
        ),
    )
```

I also created an `AlreadyInWatchlistError` exception to clearly indicate when a duplicate watchlist entry is attempted.

```python
class AlreadyInWatchlistError(Exception):
    """Raised when a film is already in the user's watchlist."""
    pass
```

Finally, I updated `add_to_watchlist()` to check whether the user already has the film in their watchlist before creating a new entry.

```python
def add_to_watchlist(user_id, film_id):
    ...
    existing = WatchlistEntry.query.filter_by(
        user_id=user_id,
        film_id=film_id,
    ).first()

    if existing:
        raise AlreadyInWatchlistError(
            f"Film '{film_id}' is already in this user's watchlist"
        )
```

If a matching watchlist entry already exists, the function raises `AlreadyInWatchlistError` instead of inserting a duplicate record.

To keep the implementation consistent with the rest of the codebase, I modeled this approach after the existing `add_to_collection()` service, which follows a similar pattern of checking for an existing record before creating a new one.

### How I verified it

I verified this behavior using `test_film_already_inside_watchlist()` in `tests/test_watchlist.py`, confirming that duplicate entries correctly raise the expected exception.

---

# Comment 3 — Missing Test

### What I changed

I added a new test file, `tests/test_watchlist.py`, covering the watchlist service.

The tests verify:

* Adding a film to a watchlist successfully.

  I implemented `test_add_to_watchlist()` which adds a film by id. This test verifies that the watchlist contains the expected film after it has been added and that the returned titles include the sample film.

* Attempting to add the same film twice raises `AlreadyInWatchlistError`.

* Attempting to add a nonexistent `film_id` is handled correctly.

  I added `test_add_to_watchlist_nonexistent_film()` which verifies that attempting to add a film ID that does not exist raises the expected exception. I modeled this after the existing collection service tests that validate invalid IDs.

* `add_to_watchlist()` behaves as expected under normal and error conditions.

The test for a nonexistent `film_id` was modeled after the existing service tests that validate invalid IDs, following the same testing structure and assertions used elsewhere in the project.

### How I verified it

I ran each test individually before running the complete test suite to ensure every test passed successfully.

---

# Comment 4 — Default Visibility

### My position

**I agree that watchlists should default to public.**

### Reasoning

CineLog is designed to encourage users to discover films through other people's activity. Making watchlists public by default makes it easier for users to browse recommendations, share what they plan to watch, and engage with the community. Users who prefer more privacy should still have the option to make their watchlist private at any time.

### Trade-offs acknowledged

Making watchlists private by default would better protect user privacy and require users to intentionally share their watchlists. However, because CineLog emphasizes movie discovery and social interaction, a public default better supports the platform's primary goal while still allowing users to change the visibility setting if they choose.

---

# Comment 5 — Sort Order

### My position

**I agree with the reviewer that "Date Added" should be the default sort order.**

### Reasoning

Most users return to their watchlist to continue watching or manage films they have recently saved. Showing the newest additions first makes recent activity immediately visible, reducing the time users spend searching for newly added films. This follows common user expectations across movie, shopping, and bookmarking applications.

### Response to the reviewer's suggestion

I agree with the maintainer's point that users generally want to see what they added most recently. A chronological order prioritizes the films that are most likely to be relevant during everyday use, making the watchlist feel more responsive and easier to navigate than an alphabetical list.

---

# Comment 6 — Rebase

### What conflicted

During the rebase, there was a conflict because one branch stored `film_id` as an integer while the updated schema stored film_id values as UUID strings.

### How I resolved it

I resolved the conflict by updating the watchlist model to consistently use UUID strings for `film_id`, matching the current database schema used throughout the project.

### How I verified it

After resolving the conflict, I completed the rebase successfully, confirmed there were no remaining merge conflicts, and reran the relevant tests to verify the feature still worked correctly.

---

# Comment 7 — `remove_from_watchlist()`

### What I changed

I implemented `remove_from_watchlist()` to allow users to remove a film from their watchlist. The function searches for a matching watchlist entry using the user ID and film ID. If an entry is found, it is deleted from the database. If the film is not present in the user's watchlist, the function raises the appropriate exception instead of attempting to delete a nonexistent record.

To keep the implementation consistent with the rest of the project, I followed the same service layer pattern used by the existing watchlist and collection services, where database operations are validated before being executed and meaningful exceptions are raised for error conditions.

### How I verified it

I added two tests to tests/test_watchlist.py:

* `test_remove_film_from_watchlist()` verifies that a film is successfully removed from a user's watchlist.

* `test_remove_film_not_in_watchlist()` verifies that attempting to remove a film that is not in the user's watchlist raises the expected exception instead of silently succeeding.

I ran both tests individually and then executed the complete test suite to confirm the removal functionality worked correctly without affecting existing watchlist behavior.

--- 

# Comment 8 — Watchlist Visibility Endpoint

### What I changed

I added a `PATCH` route, `update_watchlist_publicity()`, that allows a user to update the visibility of a watchlist.

TThe route accepts a `watchlist_id` identifying the watchlist and a `public` boolean parameter. Setting public=True makes the watchlist public, while public=False makes it private. The route passes these values to `handle_watchlist_publicity()` in `services/watchlist_service.py`, which updates the selected watchlist accordingly.

New watchlists default to `public=True`. If the provided watchlist ID does not exist or no ID is supplied, the service raises the appropriate exception instead of updating the database.

### How a caller uses it

A client sends a `PATCH` request with the desired visibility:

```json
{
    "watchlist_id": "id of the watchlist being changed",
    "public": false
}
```

Setting `"public": false` makes the watchlist private, while `"public": true` makes it public.

### How I verified it

I added `test_handle_watchlist_publicity()` to `tests/test_watchlist.py`. The test verifies that the visibility updates correctly by first setting the watchlist to private and then back to public using the `public` parameter.

```python
handle_watchlist_publicity(
    user_id=sample_user,
    watchlist_id=sample_watchlist,
    public=False,
)
assert Watchlist.query.get(sample_watchlist).public is False

handle_watchlist_publicity(
    user_id=sample_user,
    watchlist_id=sample_watchlist,
    public=True,
)
assert Watchlist.query.get(sample_watchlist).public is True
```

This confirms that the service correctly updates the watchlist to the requested visibility state.

---

# PR Description

## Overview

This pull request adds the Watchlist feature to CineLog, allows users to save films they want to watch later, prevents duplicate entries, and supports configurable watchlist visibility.

## Design Decisions

* **Default Visibility:** Watchlists are public by default to encourage movie discovery and sharing within the CineLog community while still allowing users to make their watchlists private.
* **Default Sort Order:** Watchlists are sorted by **Date Added**, ensuring that recently saved films appear first since users typically revisit the newest items on their list.

## Manual Testing

1. Create or log into a user account.
2. Add a film to the watchlist.
3. Verify the film appears in the watchlist.
4. Attempt to add the same film again and confirm the duplicate is rejected.
5. Remove the film and verify it no longer appears in the watchlist.
6. Attempt to remove the same film again and verify the expected error is returned.
7. Add multiple films and verify they appear in Date Added order.
8. Send a PATCH request with `public=false` and verify the watchlist becomes private.
9. Send another PATCH request with `public=true` and verify it becomes public again.
from repository.users import get_user_by_email
from unittest.mock import MagicMock

def test_get_user_by_email_not_found(db):
    email = "nonexistent@example.com"
    user = get_user_by_email(email, db)
    assert user is None
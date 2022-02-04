"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
from datetime import datetime

# bcrypt = Bcrypt()
# db = SQLAlchemy()

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        # Adding user for other testing:
        msg = Message(text="Hello World", timestamp=datetime.utcnow(), user=u)

        db.session.add(msg)
        db.session.commit()
        self.msg = msg
        self.u = u

    # TODO - need to look at the super
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_basic_msg(self):
        self.assertIn("Hello World", self.msg.text)
        self.assertEqual(self.u.id, self.msg.user_id) 

    def test_msg_likes(self):
        self.u.likes.append(self.msg)

        like = Likes.query.filter(Likes.user_id == self.u.id).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].messsage_id, self.msg.id)


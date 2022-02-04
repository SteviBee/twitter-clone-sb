"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py
# For model tests, you can simply verify that models have the attributes you expect, 
# and write tests for any model methods.

import os
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
# from flask_bcrypt import Bcrypt
# from flask_sqlalchemy import SQLAlchemy

# bcrypt = Bcrypt()
# db = SQLAlchemy()

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        # Adding user for other testing:
        userA = User.signup("User1", "email@test.com", "password", None)
        db.session.commit()
        self.userA = userA

    # TODO - need to look at the super
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        u3 = User(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD3"
        )

        # Populating following so to be able to test is_following()
        u.following.append(u2)
        u.followers.append(u3)

        db.session.add_all([u, u2, u3])
        db.session.commit()

        # User should have no messages & one follower
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 1)
        self.assertIn("test@test.com", u.email)
        self.assertIn("testuser", u.username)
        self.assertIn("HASHED_PASSWORD", u.password)
        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")
        self.assertTrue(u.is_following(u2))
        self.assertFalse(u.is_following(u3))
        self.assertTrue(u.is_followed_by(u3))
        self.assertFalse(u.is_followed_by(u2))

        # Testing User signup 
        u4 = User.signup(
            username="testuser4",
            password="HASH_P4",
            email="test4@test.com",
            image_url="www.fakeimg.com",
        )

        # db.session.add(u4) - TODO WHY?
        db.session.commit()
        self.assertIsInstance(u4, User)

        # Creating fail add
        with self.assertRaises(IntegrityError):
            u5 = User.signup(
                username="testuser4",
                password="HASH_P4",
                email="test4@test.com",
                image_url="www.fakeimg.com",
            ) 
            db.session.commit()
        
    # Testing AUTH:
    def test_valid_auth(self):
        
        testlogin = User.authenticate(self.userA.username, "password")        
        self.assertEqual(testlogin, self.userA)
        Invalid_password = User.authenticate(self.userA.username, "BAD")
        self.assertFalse(Invalid_password)
        Invalid_user = User.authenticate("bob", "password")
        self.assertFalse(Invalid_user)


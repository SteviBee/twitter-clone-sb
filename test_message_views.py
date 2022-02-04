"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

            resp = c.get("/messages/new")
            self.assertEqual(resp.status_code, 200)

    def test_add_no_session(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99222224 # user does not exist

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_show_message(self):
        """testing show and other routes"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Add a message and the query it:
            resp = c.post("/messages/new", data={"text": "Hello2"})
            msg = Message.query.one()
            
            resp = c.get(f"/messages/{msg.id}")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(msg.text, str(resp.data))

            # Invalid message:
            resp = c.get("/message/9923432")
            self.assertEqual(resp.status_code, 404)


            # TEST DELETE:
            resp = c.post("/messages/new", data={"text": "DELETE ME"})
            msg2 = Message.query.get(msg.id + 1)
            self.assertIsInstance(msg2, Message)

            resp = c.post(f"/messages/{msg2.id}/delete")
            self.assertFalse(Message.query.get(msg2.id))

            self.assertEqual(resp.status_code, 302)

            # TEST FAIL Like a message:
            resp = c.post(f'/users/add_like/{msg.id}')
            self.assertEqual(resp.status_code, 200)

            # TEST SUCCESS Like a message:
            # like = Likes(user_id=self.testuser.id, message_id=msg.id) 
            # db.session.add(like)           
            # db.session.commit()

            # resp = c.post(f'/users/add_like/{msg.id}')
            # self.assertEqual(resp.status_code, 302)

    def test_no_auth_delete(self):
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg3 = Message(id=1234, text="DONT WORK", user_id=self.testuser.id)
            db.session.add(msg3)
            db.session.commit()

            resp = c.post(f"/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

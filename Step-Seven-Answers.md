# Step Seven: Research and Understand Login Strategy
## Look over the code in app.py related to authentication.

1. How is the logged in user being kept track of?
    -   stored in flask-session AND in a flask global class. Session stores it across requests, but the global class is good for the app context. 
2. What is Flask’s g object?
    - A "global" flask object. Used to store the users data also the application level data like a proxy. 
3. What is the purpose of add_user_to_g?
    - Every request pushes a new application context therefore the global class must be defined with every request. Add_user_to_g does this.
4. What does @app.before_request mean?
    - it runs before every request!
5. Further research - best use cases for g-object vs session. 
import time
from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import random

# Database file name
DATABASE_FILE = "my_database.db"

EMOTION_DICT = {"Angry" : 4, "Disgust": 5, "Fear": 27, "Happy": 26, "Sad": 25, "Surprise": 33, "Neutral": 32}

app = Flask(__name__)
CORS(app)

def authenticate(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Execute a query to fetch the user's password based on the provided username
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        # If the username exists, check if the provided password matches the fetched password
        if user_data[0] == password:
            return True  # Authentication successful
    return False  # Authentication failed


def insert_user(user_id, username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    existing_user = c.fetchone()
    if existing_user:
        print("User with username '{}' already exists. Skipping insertion.".format(username))
    else:
        c.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (user_id, username, password))
        print("User '{}' inserted successfully.".format(username))

        conn.commit()

    conn.close()

def generate_unique_user_id(cursor):
    while True:
        user_id = random.randint(1000, 9999) 
        cursor.execute("SELECT COUNT(*) FROM users WHERE id=?", (user_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            return user_id

def insert_user(username, password):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = c.fetchone()

        if existing_user:
            print("User with username '{}' already exists. Skipping insertion.".format(username))
            return False  
        
        user_id = generate_unique_user_id(c)

        c.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (user_id, username, password))
        conn.commit()

        print("User '{}' inserted successfully with ID {}".format(username, user_id))
        return True 

    except Exception as e:
        print(f"Error inserting user: {e}")
        return False

    finally:
        if conn:
            conn.close()

def insert_emotion(user_id, emotion, confidence, additional_data=None):
    conn = connect_db()
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO emotions (user_id, timestamp, emotion, confidence, additional_data) VALUES (?, ?, ?, ?, ?)",
        (user_id, timestamp, emotion, confidence, additional_data)
    )
    conn.commit()
    close_db(conn)

# Function to connect to the database
def connect_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Set row factory for dictionary-like access
    return conn


# Function to close the database connection
def close_db(conn):
    if conn:
        conn.close()


@app.route('/signup', methods=['GET'])
def signup_fun():
    # Get username and password from request params
    username = request.args.get('username')
    password = request.args.get('password')

    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()

        # Insert user and handle potential errors
        success = insert_user(username, password)
        if success:
            return jsonify({"message": "User created successfully"}), 201
        else:
            return jsonify({"error": "User creation failed"}), 400  # Adjust error code as needed

    except Exception as e:
        print(f"Error inserting user: {e}")
        return jsonify({"error": "Internal server error"}), 500  # Generic error for UI

    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['GET'])
def login_fun():
    username = request.args.get('username')
    password = request.args.get('password')

    print(username)
    print(password)

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = c.fetchone()

        if not existing_user: return jsonify({"error": "User not found"}), 500

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password,))
        user = c.fetchone()

        if user:
            c.execute("SELECT id, username, password FROM users WHERE username=?", (username,))
            user_data = c.fetchone()
            user_id, username, password = user_data

            return {
                "userid": user_id,
                "username": username,
                "password": password
            }
        else : jsonify({"error": "Username or Password Incorrect"}), 500
        
    except Exception as e:
        print(f"Error inserting user: {e}")
        return jsonify({"error": "Internal server error"}), 500  # Generic error for UI

    finally:
        if conn:
            conn.close()

# Read all users endpoint
@app.route("/users", methods=["GET"])
def read_users():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    close_db(conn)

    return jsonify([dict(row) for row in users])  # Convert rows to dictionaries


# Read a specific user by ID endpoint
@app.route("/users/<int:user_id>", methods=["GET"])
def read_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    close_db(conn)

    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user))  # Convert row to dictionary


# Create a new user endpoint
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("age"):
        return jsonify({"error": "Missing required fields"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, age) VALUES (?, ?)", (data["name"], data["age"])
    )
    conn.commit()
    close_db(conn)

    return jsonify({"message": "User created successfully"}), 201


@app.route("/receive_emotion", methods=["POST"])
def receive_emotion():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    emotion = data.get("emotion")

    if not username or not password or not emotion:
        return jsonify({"error": "Missing required fields"}), 400

    # Authenticate user
    if not authenticate(username, password):
        return jsonify({"error": "Authentication failed"}), 401
    
    try:
        insert_emotion(user_id=1, emotion=emotion, confidence=1.0)
        # DATA TO SUMMERIZED FROM HERE
        return jsonify({"message": "Emotion recorded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/latestemotion', methods=['GET'])
def get_latest_emotion():
    # Get username and password from request params
    username = request.args.get('username')
    password = request.args.get('password')

    # Connect to the database
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # Query to fetch the user ID based on the provided username and password
    query = """
    SELECT id FROM users
    WHERE username = ? AND password = ?
    """
    c.execute(query, (username, password))
    user_id = c.fetchone()

    # Check if user exists
    if user_id:
        user_id = user_id[0]  # Extract user ID from the fetched tuple

        # Query to fetch the latest emotion entry for the specified user ID
        emotion_query = """
        SELECT * FROM emotions
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """
        c.execute(emotion_query, (user_id,))
        result = c.fetchone()

        # Close the connection
        conn.close()

        # Check if result is not None
        if result:
            # Create a dictionary with column names as keys and fetched values as values
            emotion_data = {
                "id": result[0],
                "user_id": result[1],
                "timestamp": result[2],
                "emotion": result[3],
                "confidence": result[4],
                "additional_data": result[5],
                "emotion_id": EMOTION_DICT[result[3]]
            }
            # Return the fetched data as JSON response
            return jsonify(emotion_data)
        else:
            # If no data found, return a message
            return jsonify({"message": "No emotion entry found for the specified user."}), 404
    else:
        # If user does not exist or provided credentials are incorrect, return a message
        return jsonify({"message": "Invalid username or password."}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
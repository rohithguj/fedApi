from flask import Flask, jsonify, request
import sqlite3

# Database file name
DATABASE_FILE = "my_database.db"

app = Flask(__name__)


# Function to connect to the database
def connect_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Set row factory for dictionary-like access
    return conn


# Function to close the database connection
def close_db(conn):
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


if __name__ == "__main__":
    app.run(debug=True, port=8080)
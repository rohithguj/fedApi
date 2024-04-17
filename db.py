import sqlite3

from server import insert_user

# Define database file name
db_file = "my_database.db"

# Connect to the database
conn = sqlite3.connect(db_file)

# Create a cursor object
c = conn.cursor()

# Define table creation statements (replace with your desired column names and data types)
table1_sql = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  password TEXT
)
"""

table2_sql = """
CREATE TABLE IF NOT EXISTS emotions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  timestamp DATETIME,
  interval TEXT,
  emotion TEXT,
  confidence REAL,
  additional_data TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
)
"""

# Execute the table creation statements
c.execute(table1_sql)
c.execute(table2_sql)

# Commit changes to the database (optional, ensures data persistence)
conn.commit()

# Close the connection
conn.close()

print("Tables created successfully!")

insert_user(1, "Admin", "Pass@321")
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to connect to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='geolocation_db',
        user='root',
        password='yuvrajA20)^'
    )

# Function to retrieve existing locations from the MySQL database
def get_existing_locations():
    existing_locations = []
    try:
        connection = get_db_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT latitude, longitude FROM locations")
            existing_locations = cursor.fetchall()  # Get all records
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    return existing_locations

@app.route('/location', methods=['POST'])
def location():
    data = request.json
    latitude = data['latitude']
    longitude = data['longitude']
    
    # Fetch existing locations from the database
    existing_locations = get_existing_locations()
    
    # Check if user's coordinates match any existing coordinates
    matches = any(
        round(lat, 3) == round(latitude, 3) and round(long, 3) == round(longitude, 3)
        for lat, long in existing_locations
    )
    
    return jsonify({'matches': matches})

@app.route('/existing-coordinates', methods=['GET'])
def existing_coordinates():
    existing_locations = get_existing_locations()
    # Return as a JSON array
    return jsonify(existing_locations)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import mysql.connector
from math import radians, sin, cos, sqrt, asin
from flask_cors import CORS
import os

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='geolocation_db',
        user='root',
        password='yuvrajA20)^'
    )

# Haversine formula to calculate the distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c

# Fetch all coordinates from the database
@app.route('/all-coordinates', methods=['GET'])
def all_coordinates():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, latitude, longitude FROM locations")
        data = cursor.fetchall()
        return jsonify(data)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# Calculate distance between two points
@app.route('/calculate-distance', methods=['POST'])
def calculate_distance():
    data = request.json
    lat1 = data.get('lat1')
    lon1 = data.get('lon1')
    lat2 = data.get('lat2')
    lon2 = data.get('lon2')

    # Input validation
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return jsonify({"error": "Missing latitude or longitude values."}), 400

    try:
        distance = haversine(lat1, lon1, lat2, lon2)
        return jsonify({"distance": distance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Find nearby places within the specified radius
@app.route('/nearby-places', methods=['POST'])
def nearby_places():
    data = request.json
    user_lat = data.get('latitude')
    user_lon = data.get('longitude')
    radius = data.get('radius')

    # Input validation
    if user_lat is None or user_lon is None or radius is None:
        return jsonify({"error": "Missing latitude, longitude, or radius."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, latitude, longitude FROM locations")
        places = cursor.fetchall()

        nearby = []
        for place in places:
            distance = haversine(user_lat, user_lon, place['latitude'], place['longitude'])
            if distance <= radius:
                nearby.append({'name': place['name'], 'distance': distance})

        return jsonify(nearby)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

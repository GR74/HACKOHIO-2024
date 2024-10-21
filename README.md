# HACKOHIO-2024

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Distance Calculator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
            color: #333;
        }
        h1 {
            color: #007bff;
        }
        #distances {
            margin-top: 20px;
        }
        .distance-item {
            margin-bottom: 10px;
            padding: 10px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Distances from Parent User's Location</h1>
    <p>Below are the distances between the parent user's location and the existing locations in the database.</p>

    <div id="distances">
        Loading distances...
    </div>

    <script>
        // Function to fetch distances from the server
        function fetchDistances() {
            fetch('http://127.0.0.1:5000/calculate-distances')
                .then(response => response.json())
                .then(data => {
                    const distancesDiv = document.getElementById('distances');
                    distancesDiv.innerHTML = ''; // Clear any existing content

                    if (data.error) {
                        distancesDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
                    } else if (data.length === 0) {
                        distancesDiv.innerHTML = '<p>No locations found.</p>';
                    } else {
                        data.forEach(item => {
                            distancesDiv.innerHTML += `
                                <div class="distance-item">
                                    <strong>Location:</strong> ${item.name} <br>
                                    <strong>Distance:</strong> ${item.distance.toFixed(2)} km
                                </div>
                            `;
                        });
                    }
                })
                .catch(error => {
                    console.error('Error fetching distances:', error);
                    document.getElementById('distances').innerHTML = '<p style="color:red;">Failed to load distances. Please try again later.</p>';
                });
        }

        // Fetch distances on page load
        window.onload = fetchDistances;
    </script>
</body>
</html>














from flask import Flask, jsonify
import mysql.connector
from math import radians, sin, cos, sqrt, asin

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='geolocation_db',
        user='root',
        password='root_password'
    )

# Haversine formula to calculate the distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c

# Function to retrieve the parent user's geolocation
def get_parent_geolocation():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT latitude, longitude FROM users WHERE id = 1")  # Assuming the parent user has an ID of 1
        parent_location = cursor.fetchone()
        return parent_location['latitude'], parent_location['longitude']
    except mysql.connector.Error as err:
        return None, None
    finally:
        cursor.close()
        conn.close()

# Function to retrieve existing locations from the database
def get_existing_locations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, latitude, longitude FROM locations")
        locations = cursor.fetchall()
        return locations
    except mysql.connector.Error as err:
        return []
    finally:
        cursor.close()
        conn.close()

# Route to calculate distances between parent user and all existing locations
@app.route('/calculate-distances', methods=['GET'])
def calculate_distances():
    parent_lat, parent_lon = get_parent_geolocation()
    
    if parent_lat is None or parent_lon is None:
        return jsonify({"error": "Could not retrieve parent user's geolocation"}), 500

    existing_locations = get_existing_locations()

    distances = []
    for location in existing_locations:
        distance = haversine(parent_lat, parent_lon, location['latitude'], location['longitude'])
        distances.append({
            'name': location['name'],
            'distance': distance
        })

    return jsonify(distances)

if __name__ == '__main__':
    app.run(debug=True)


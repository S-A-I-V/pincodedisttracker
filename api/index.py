from flask import Flask, request, jsonify, render_template_string
from geopy.distance import geodesic
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Your OpenCage API key
OPEN_CAGE_API_KEY = '6152f15cb29943278b9064d851553d5c'

def get_coords(pincode):
    url = f'https://api.opencagedata.com/geocode/v1/json?q={pincode}&key={OPEN_CAGE_API_KEY}&countrycode=IN'
    response = requests.get(url)
    data = response.json()
    if data['results']:
        coords = data['results'][0]['geometry']
        return coords['lat'], coords['lng']
    return None, None

# HTML content to serve
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Distance Calculator (India)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #666;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #218838;
        }
        .result {
            margin-top: 10px;
            color: #333;
            font-size: 18px;
            text-align: center;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Distance Calculator (India)</h1>
    <label for="fromPincode">From Pincode:</label>
    <input type="text" id="fromPincode" placeholder="Enter From Pincode">

    <label for="toPincode">To Pincode:</label>
    <input type="text" id="toPincode" placeholder="Enter To Pincode">

    <button onclick="getDistance()">Get Distance</button>

    <div class="result" id="result"></div>
</div>

<script>
    function getDistance() {
        const fromPincode = document.getElementById('fromPincode').value;
        const toPincode = document.getElementById('toPincode').value;
        const resultDiv = document.getElementById('result');

        if (fromPincode === '' || toPincode === '') {
            resultDiv.innerHTML = "Please enter both pin codes.";
            return;
        }

        // Fetch distance from the server
        fetch(`/get_distance?from=${fromPincode}&to=${toPincode}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = "Invalid pincode.";
                } else {
                    resultDiv.innerHTML = `Distance: ${data.distance.toFixed(2)} km`;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = "Unable to fetch the distance.";
                console.error(error);
            });
    }
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_content)

@app.route('/get_distance', methods=['GET'])
def get_distance():
    from_pincode = request.args.get('from')
    to_pincode = request.args.get('to')

    # Get coordinates for the pin codes using OpenCage API
    from_lat, from_lng = get_coords(from_pincode)
    to_lat, to_lng = get_coords(to_pincode)

    if from_lat is None or to_lat is None:
        return jsonify({'error': 'Invalid pincode'}), 400

    # Extract latitude and longitude
    from_coords = (from_lat, from_lng)
    to_coords = (to_lat, to_lng)

    # Calculate the distance in kilometers
    distance = geodesic(from_coords, to_coords).kilometers

    return jsonify({'distance': distance})

if __name__ == '__main__':
    app.run(debug=True)

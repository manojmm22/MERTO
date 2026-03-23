"""
Metro Arrival Predictor - Flask Web Application

A web application that uses a Perceptron-based model to predict
metro train arrival times at each station.
"""

from flask import Flask, render_template, request, jsonify
from perceptron_model import get_model, reset_model
from database import get_database


app = Flask(__name__)
app.config['SECRET_KEY'] = 'metro-arrival-predictor-secret-key-2024'


# ==================== Routes ====================

@app.route('/')
def index():
    """Main page of the application."""
    return render_template('index.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    API endpoint for making predictions.
    
    Expected JSON payload:
    {
        "departure_time": "HH:MM",
        "distance": float,
        "speed": float,
        "dwell_time": float
    }
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'JSON body required'}), 400
        
        # Validate required fields
        required_fields = ['departure_time', 'distance', 'speed', 'dwell_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract values
        departure_time = data['departure_time']
        distance = float(data['distance'])
        speed = float(data['speed'])
        # Convert dwell time from minutes to seconds (UI sends minutes, model expects seconds)
        dwell_time_minutes = float(data['dwell_time'])
        dwell_time = dwell_time_minutes * 60
        
        # Validate ranges
        if distance <= 0 or distance > 50:
            return jsonify({'error': 'Distance must be between 0 and 50 km'}), 400
        if speed <= 0 or speed > 150:
            return jsonify({'error': 'Speed must be between 0 and 150 km/h'}), 400
        if dwell_time_minutes < 0 or dwell_time_minutes > 60:
            return jsonify({'error': 'Dwell time must be between 0 and 60 minutes'}), 400
        
        # Get model and make prediction
        model = get_model()
        arrival_time, travel_time = model.predict(departure_time, distance, speed, dwell_time)
        
        # Save to database
        db = get_database()
        prediction_id = db.save_prediction(
            departure_time=departure_time,
            distance=distance,
            speed=speed,
            dwell_time=dwell_time,
            predicted_arrival=arrival_time,
            travel_time=travel_time
        )
        
        return jsonify({
            'success': True,
            'prediction': {
                'id': prediction_id,
                'departure_time': departure_time,
                'distance': distance,
                'speed': speed,
                'dwell_time': dwell_time_minutes,  # Return in minutes for user clarity
                'predicted_arrival': arrival_time,
                'travel_time': travel_time
            }
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get all stations from the database."""
    try:
        db = get_database()
        stations = db.get_all_stations()
        return jsonify({'success': True, 'stations': stations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/journey', methods=['POST'])
def predict_journey():
    """
    Predict arrival times for an entire journey.
    
    Expected JSON payload:
    {
        "departure_time": "HH:MM",
        "speed": float,
        "dwell_time": float
    }
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            data = {}
        
        departure_time = data.get('departure_time', '08:00')
        speed = float(data.get('speed', 40))
        # Convert dwell time from minutes to seconds (UI sends minutes, model expects seconds)
        dwell_time_minutes = float(data.get('dwell_time', 0.5))
        dwell_time = dwell_time_minutes * 60
        
        if speed <= 0 or speed > 150:
            return jsonify({'error': 'Speed must be between 0 and 150 km/h'}), 400
        if dwell_time_minutes < 0 or dwell_time_minutes > 60:
            return jsonify({'error': 'Dwell time must be between 0 and 60 minutes'}), 400
        
        # Get stations from database
        db = get_database()
        stations = db.get_all_stations()
        
        # Build stations data for journey prediction
        stations_data = []
        for station in stations:
            if station['order_index'] > 1:  # Skip first station (starting point)
                stations_data.append((
                    station['name'],
                    station['distance_from_previous']
                ))
        
        # Get model and predict journey
        model = get_model()
        journey_results = model.predict_journey(
            departure_time=departure_time,
            stations_data=stations_data,
            base_speed=speed,
            dwell_time=dwell_time
        )
        
        # Format results
        results = []
        for station_name, arrival_time, travel_time, distance in journey_results:
            results.append({
                'station': station_name,
                'arrival': arrival_time,
                'travel_time': travel_time,
                'distance': distance
            })
        
        return jsonify({
            'success': True,
            'journey': {
                'departure': departure_time,
                'stops': results
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get prediction history from database."""
    try:
        limit = request.args.get('limit', 20, type=int)
        db = get_database()
        history = db.get_prediction_history(limit)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get database statistics."""
    try:
        db = get_database()
        stats = db.get_statistics()
        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/train', methods=['POST'])
def train_model():
    """
    Retrain the Perceptron model.
    """
    try:
        reset_model()
        get_model()
        return jsonify({'success': True, 'message': 'Model trained successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize database on startup
    db = get_database()
    print("Database initialized successfully!")
    
    # Start the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)

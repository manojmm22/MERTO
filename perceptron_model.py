"""
Perceptron Model for Metro Train Arrival Time Prediction

This module implements a single-layer Perceptron (linear model) to predict
metro train arrival times based on:
- Starting departure time
- Distance between stations
- Average train speed
- Dwell time at stations

Uses pure Python (no numpy dependency)
"""

import random


class PerceptronModel:
    """
    A Perceptron-based linear model for predicting metro train arrival times.
    
    The model learns weights for: distance, speed, dwell_time, and time_of_day
    to predict the travel time between stations.
    """
    
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        """
        Initialize the Perceptron model.
        
        Args:
            learning_rate: Step size for weight updates
            n_iterations: Number of training epochs
        """
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
        self.is_trained = False
        
    def _normalize_time(self, time_str):
        """Convert time string to minutes from midnight."""
        try:
            parts = time_str.strip().split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return hours * 60 + minutes
        except (ValueError, IndexError):
            return 0
    
    def _generate_training_data(self, n_samples=500):
        """
        Generate synthetic training data with realistic metro parameters.
        
        Returns:
            X: Feature list [departure_time_norm, distance, speed, dwell_time]
            y: Target values (travel time in minutes)
        """
        X = []
        y = []
        
        for _ in range(n_samples):
            # Generate random values within realistic ranges
            departure_hour = random.randint(5, 23)
            departure_minute = random.randint(0, 59)
            departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
            departure_norm = self._normalize_time(departure_time)
            
            # Distance between stations: 0.5 to 5 km
            distance = random.uniform(0.5, 5.0)
            
            # Average speed: 20 to 80 km/h
            speed = random.uniform(20, 80)
            
            # Dwell time: 10 to 60 seconds
            dwell_time = random.uniform(10, 60)
            
            # Calculate actual travel time (in minutes)
            # travel_time = (distance / speed) * 60 + (dwell_time / 60)
            travel_time = (distance / speed) * 60 + (dwell_time / 60)
            
            # Add some noise to make it realistic
            noise = random.uniform(-0.5, 0.5)
            travel_time = max(0.5, travel_time + noise)
            
            # Normalize features for better training
            X.append([
                departure_norm / 1440.0,  # Normalize time to [0,1]
                distance / 10.0,           # Normalize distance to [0,1] (max 10km)
                speed / 100.0,             # Normalize speed to [0,1] (max 100km/h)
                dwell_time / 60.0          # Normalize dwell time to [0,1] (max 60s)
            ])
            y.append(travel_time)
        
        return X, y
    
    def _dot_product(self, x, weights):
        """Calculate dot product of two lists."""
        return sum(xi * wi for xi, wi in zip(x, weights))
    
    def train(self):
        """Train the Perceptron model using generated synthetic data."""
        print("Generating training data...")
        n_samples = 500
        X, y = self._generate_training_data(n_samples=n_samples)
        
        n_samples = len(X)
        n_features = len(X[0])
        
        # Initialize weights and bias with small random values
        random.seed(42)
        self.weights = [random.uniform(-0.01, 0.01) for _ in range(n_features)]
        self.bias = 0.0
        
        print(f"Training Perceptron with {n_samples} samples...")
        
        # Training loop
        for epoch in range(self.n_iterations):
            total_error = 0
            for idx in range(n_samples):
                x_i = X[idx]
                target = y[idx]
                
                # Forward pass: calculate prediction
                y_pred = self._dot_product(x_i, self.weights) + self.bias
                
                # Calculate error
                error = target - y_pred
                total_error += error ** 2
                
                # Update weights and bias
                for j in range(n_features):
                    self.weights[j] += self.learning_rate * error * x_i[j]
                self.bias += self.learning_rate * error
            
            if (epoch + 1) % 200 == 0:
                mse = total_error / n_samples
                print(f"Epoch {epoch + 1}/{self.n_iterations}, MSE: {mse:.4f}")
        
        self.is_trained = True
        print("Training complete!")
        print(f"Final weights: {self.weights}")
        print(f"Final bias: {self.bias}")
        
        return self
    
    def _features(self, departure_time, distance, speed, dwell_time):
        """Build normalized feature vector (must match training)."""
        departure_norm = self._normalize_time(departure_time) / 1440.0
        return [
            departure_norm,
            distance / 10.0,
            speed / 100.0,
            dwell_time / 60.0,
        ]

    def predict(self, departure_time, distance, speed, dwell_time):
        """
        Predict arrival time at the next station using the trained linear model.
        
        Args:
            departure_time: String in "HH:MM" format
            distance: Distance in kilometers
            speed: Average speed in km/h
            dwell_time: Dwell time in seconds
            
        Returns:
            Predicted arrival time as string "HH:MM"
        """
        if not self.is_trained:
            self.train()

        x = self._features(departure_time, distance, speed, dwell_time)
        travel_time = self._dot_product(x, self.weights) + self.bias
        travel_time = max(0.5, float(travel_time))
        
        departure_minutes = self._normalize_time(departure_time)
        total_mins = int(round(departure_minutes + travel_time)) % 1440
        hours = total_mins // 60
        minutes = total_mins % 60
        arrival_time = f"{hours:02d}:{minutes:02d}"
        
        return arrival_time, round(travel_time, 2)
    
    def predict_journey(self, departure_time, stations_data, base_speed=40, dwell_time=30):
        """
        Predict arrival times for an entire journey through multiple stations.
        
        Args:
            departure_time: Starting time "HH:MM"
            stations_data: List of (station_name, distance_from_previous) tuples
            base_speed: Default speed in km/h
            dwell_time: Default dwell time in seconds
            
        Returns:
            List of (station_name, arrival_time) tuples
        """
        if not self.is_trained:
            self.train()
        
        results = []
        current_time = departure_time
        
        for station_name, distance in stations_data:
            arrival_time, travel_time = self.predict(current_time, distance, base_speed, dwell_time)
            results.append((station_name, arrival_time, round(travel_time, 2), distance))
            current_time = arrival_time
        
        return results


# Singleton instance
_model = None


def get_model():
    """Get or create the singleton Perceptron model instance."""
    global _model
    if _model is None:
        _model = PerceptronModel(learning_rate=0.01, n_iterations=1000)
        _model.train()
    return _model


def reset_model():
    """Clear the cached model so the next get_model() trains a fresh instance."""
    global _model
    _model = None


if __name__ == "__main__":
    # Test the model
    model = PerceptronModel()
    model.train()
    
    # Test prediction
    arrival, travel_time = model.predict("08:00", 2.5, 40, 30)
    print(f"\nTest Prediction:")
    print(f"Departure: 08:00")
    print(f"Distance: 2.5 km")
    print(f"Speed: 40 km/h")
    print(f"Dwell time: 30 seconds")
    print(f"Predicted arrival: {arrival}")
    print(f"Travel time: {travel_time} minutes")

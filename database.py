"""
Database Module for Metro Arrival Predictor

This module handles all SQLite database operations including:
- Station management
- Train route storage
- Prediction history
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager


class Database:
    """SQLite database manager for the Metro Arrival Predictor."""
    
    def __init__(self, db_path="metro.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Stations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    distance_from_previous REAL DEFAULT 0,
                    order_index INTEGER,
                    latitude REAL,
                    longitude REAL
                )
            ''')
            
            # Add columns if they don't exist (migration)
            try:
                cursor.execute('ALTER TABLE stations ADD COLUMN latitude REAL')
            except:
                pass
            try:
                cursor.execute('ALTER TABLE stations ADD COLUMN longitude REAL')
            except:
                pass
            
            # Train routes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS train_routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_name TEXT NOT NULL,
                    departure_time TEXT NOT NULL,
                    arrival_time TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departure_time TEXT NOT NULL,
                    distance REAL NOT NULL,
                    speed REAL NOT NULL,
                    dwell_time REAL NOT NULL,
                    predicted_arrival TEXT NOT NULL,
                    travel_time REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default metro stations if not exists (coordinates form a plausible north–east corridor)
            default_stations = [
                ("Central Station", 0, 1, 40.7128, -74.0130),
                ("Market Square", 1.2, 2, 40.7152, -74.0102),
                ("University", 2.5, 3, 40.7180, -74.0074),
                ("Tech Park", 1.8, 4, 40.7204, -74.0046),
                ("Airport Terminal", 3.5, 5, 40.7238, -74.0012),
                ("City Hall", 2.0, 6, 40.7265, -73.9984),
                ("Harbor View", 1.5, 7, 40.7290, -73.9956),
                ("Sports Complex", 2.2, 8, 40.7320, -73.9920),
                ("Convention Center", 1.8, 9, 40.7348, -73.9888),
            ]
            
            for name, distance, order_idx, lat, lng in default_stations:
                cursor.execute('''
                    INSERT OR IGNORE INTO stations (name, distance_from_previous, order_index, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, distance, order_idx, lat, lng))
            
            # Update existing stations with coordinates (keeps demo DB in sync with route geometry)
            station_coords = {
                "Central Station": (40.7128, -74.0130),
                "Market Square": (40.7152, -74.0102),
                "University": (40.7180, -74.0074),
                "Tech Park": (40.7204, -74.0046),
                "Airport Terminal": (40.7238, -74.0012),
                "City Hall": (40.7265, -73.9984),
                "Harbor View": (40.7290, -73.9956),
                "Sports Complex": (40.7320, -73.9920),
                "Convention Center": (40.7348, -73.9888),
            }
            
            for name, (lat, lng) in station_coords.items():
                cursor.execute('''
                    UPDATE stations SET latitude = ?, longitude = ? WHERE name = ?
                ''', (lat, lng, name))
            
            conn.commit()
    
    # ==================== Station Operations ====================
    
    def get_all_stations(self):
        """Get all stations ordered by their route order."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM stations ORDER BY order_index
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def add_station(self, name, distance_from_previous, order_index):
        """Add a new station to the route."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stations (name, distance_from_previous, order_index)
                VALUES (?, ?, ?)
            ''', (name, distance_from_previous, order_index))
            return cursor.lastrowid
    
    def delete_station(self, station_id):
        """Delete a station by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM stations WHERE id = ?', (station_id,))
            return cursor.rowcount > 0
    
    # ==================== Prediction Operations ====================
    
    def save_prediction(self, departure_time, distance, speed, dwell_time, 
                        predicted_arrival, travel_time):
        """
        Save a prediction to the database.
        
        Args:
            departure_time: Departure time string
            distance: Distance in km
            speed: Speed in km/h
            dwell_time: Dwell time in seconds
            predicted_arrival: Predicted arrival time
            travel_time: Travel time in minutes
            
        Returns:
            ID of the inserted record
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (departure_time, distance, speed, dwell_time, predicted_arrival, travel_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (departure_time, distance, speed, dwell_time, predicted_arrival, travel_time))
            return cursor.lastrowid
    
    def get_prediction_history(self, limit=20):
        """
        Get recent predictions.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of prediction records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM predictions 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def clear_prediction_history(self):
        """Clear all prediction history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM predictions')
            return cursor.rowcount
    
    # ==================== Route Operations ====================
    
    def save_route(self, route_name, departure_time, arrival_time):
        """Save a train route."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO train_routes (route_name, departure_time, arrival_time)
                VALUES (?, ?, ?)
            ''', (route_name, departure_time, arrival_time))
            return cursor.lastrowid
    
    def get_routes(self):
        """Get all saved routes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM train_routes ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Statistics ====================
    
    def get_statistics(self):
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM stations')
            stations_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM predictions')
            predictions_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM train_routes')
            routes_count = cursor.fetchone()[0]
            
            return {
                'stations': stations_count,
                'predictions': predictions_count,
                'routes': routes_count
            }


# Singleton instance
_db = None


def get_database():
    """Get or create the singleton database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


if __name__ == "__main__":
    # Test database operations
    db = Database()
    
    # Get stations
    stations = db.get_all_stations()
    print("Stations:", stations)
    
    # Get statistics
    stats = db.get_statistics()
    print("Statistics:", stats)

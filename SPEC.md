# Metro Train Arrival Time Prediction - Specification Document

## Project Overview
- **Project Name**: Metro Arrival Predictor
- **Type**: Web Application (Python Flask + Perceptron ML Model)
- **Core Functionality**: Predict metro train arrival times at each station using a Perceptron-based linear model
- **Target Users**: Metro transit operators, commuters, and transportation planners

## ML Model Specification

### Perceptron Model
- **Type**: Single-layer Perceptron (Linear Model)
- **Inputs (Features)**:
  1. Starting departure time (normalized to minutes from midnight)
  2. Distance between stations (in kilometers)
  3. Average train speed (in km/h)
  4. Dwell time at stations (in **minutes**, converted to seconds internally)
- **Output**: Arrival time at next station (in minutes from departure)

### Model Formula
```
arrival_time = (distance / speed * 60) + dwell_time + bias
```
Where:
- distance: km between stations
- speed: km/h average speed
- dwell_time: seconds at each station
- bias: learned offset for time of day variations

### Training Data Generation
- Synthetic training data generated with realistic metro parameters
- Training iterations: 1000 epochs
- Learning rate: 0.001

## Database Schema

### Tables
1. **stations**
   - id (INTEGER PRIMARY KEY)
   - name (TEXT)
   - distance_from_previous (REAL)
   - order_index (INTEGER)

2. **train_routes**
   - id (INTEGER PRIMARY KEY)
   - route_name (TEXT)
   - departure_time (TEXT)
   - arrival_time (TEXT)
   - created_at (TIMESTAMP)

3. **predictions**
   - id (INTEGER PRIMARY KEY)
   - departure_time (TEXT)
   - distance (REAL)
   - speed (REAL)
   - dwell_time (REAL)
   - predicted_arrival (TEXT)
   - created_at (TIMESTAMP)

## UI/UX Specification

### Layout Structure
- **Header**: App title with metro icon
- **Main Content**: Two-column layout
  - Left: Input form for prediction
  - Right: Results display
- **Footer**: Copyright and model info

### Visual Design
- **Color Palette**:
  - Primary: #1E3A5F (Deep Metro Blue)
  - Secondary: #4A90D9 (Sky Blue)
  - Accent: #F5A623 (Orange)
  - Background: #0D1B2A (Dark Navy)
  - Card Background: #1B2838 (Slate)
  - Text: #FFFFFF (White)
  - Success: #4CAF50 (Green)
- **Typography**:
  - Headings: 'Orbitron', sans-serif (tech/metro feel)
  - Body: 'Roboto', sans-serif
- **Effects**: 
  - Subtle glow on interactive elements
  - Smooth transitions (0.3s ease)
  - Card shadows

### Components
1. **Input Form**:
   - Departure time picker
   - Distance input (km)
   - Speed slider (20-80 km/h)
   - Dwell time slider (0-2 minutes) - **Updated to minutes for user-friendliness**
   - Predict button

2. **Results Panel**:
   - Predicted arrival time display
   - Visual timeline of journey
   - Train icon animation during prediction

3. **History Table**:
   - Recent predictions with timestamps
   - Database stored results

## Functionality Specification

### Core Features
1. Real-time arrival time prediction using Perceptron model
2. Database storage of all predictions
3. Station management interface
4. Prediction history viewing
5. Model parameter adjustment (speed, dwell time)

### User Interactions
1. Select departure time
2. Input/select distance between stations
3. Adjust expected train speed
4. Set dwell time at stations
5. Click predict to get arrival time
6. View prediction history from database

### Edge Cases
- Handle invalid input values
- Validate time formats
- Prevent negative predictions
- Handle database connection errors

## Acceptance Criteria
1. ✓ Perceptron model successfully predicts arrival times
2. ✓ All predictions stored in SQLite database
3. ✓ Web interface is responsive and user-friendly
4. ✓ Form validation prevents invalid inputs
5. ✓ Prediction history is retrievable from database
6. ✓ Visual feedback during prediction process

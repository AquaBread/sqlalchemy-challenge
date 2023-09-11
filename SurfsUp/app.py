# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect an existing database into a new model
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        f"/api/v1.0/stations - List of stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the most active station (last 12 months)<br/>"
        f"/api/v1.0/<start> - Temperature statistics for a start date<br/>"
        f"/api/v1.0/<start>/<end> - Temperature statistics for a date range"
    )

#################################################
# Flask Routes
#################################################

# the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    session.close()
    
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    
    return jsonify(prcp_dict)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station, Station.name).all()
    session.close()
    
    station_list = [{"Station ID": station, "Station Name": name} for station, name in stations]
    
    return jsonify(station_list)

# temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= last_year).all()
    session.close()
    
    tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in tobs_data]
    
    return jsonify(tobs_list)

# temperature statistics route for a start date
@app.route("/api/v1.0/<start>")
def temperature_start(start):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()
    session.close()
    
    temperature_stats = {
        "Minimum Temperature": results[0][0],
        "Average Temperature": results[0][1],
        "Maximum Temperature": results[0][2]
    }
    
    return jsonify(temperature_stats)

# temperature statistics route for a date range
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    
    temperature_stats = {
        "Minimum Temperature": results[0][0],
        "Average Temperature": results[0][1],
        "Maximum Temperature": results[0][2]
    }
    
    return jsonify(temperature_stats)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
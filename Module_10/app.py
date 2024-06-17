# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
from pandas.plotting import table
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# Save references to each table
station = base.classes.station
measurement = base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def home():
    return(
    f"<center><h2>Welcome to the Hawaii Climate Analysis Local API!</h2></center>"
    f"<center><h3>Select from one of the available routes: </h3></center>"
    f"<center>/api/v1.0/precipitation</center>"
    f"<center>/api/v1.0/stations</center>"
    f"<center>/api/v1.0/tobs</center>"
    f"<center>/api/v1.0/start</center>"
    f"<center>/api/v1.0/start/end</center>"
    )

# /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    # Return the previous year's precipitation as a json.
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= previousYear).all()
    
    session.close()
    # Dictionary with the dates as the keys and precipitation as the value.
    precipitation = {date: prcp for date, prcp in results}
    # jsonify
    return jsonify(precipitation)

# /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # shows a list of the stations.
    # Perform a query to retrieve the names of the stations.
    results = session.query(station.station).all()
    session.close()
    station_list = list(np.ravel(results))
    
    # convert to a json and display.
    return jsonify(station_list)
    

# api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # return the previous year's temperatures.
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the temperatures from the most active station from the past year.
    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= previousYear).all()
        
    session.close()
    
    tobs_list = list(np.ravel(results))
    
    # convert to a json and display.
    return jsonify(tobs_list)

# api/v1.0/start api/v1.0/start/end routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_stats(start=None, end=None):
    # selection statement
    selection = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    
    if not end:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection).filter(measurement.date >= start_date).all()
        
        session.close()
        
        tobs_list = list(np.ravel(results))
    
        # convert to a json and display.
        return jsonify(tobs_list)
        
    else:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        end_date = dt.datetime.strptime(end, "%m%d%Y")
        results = session.query(*selection)\
            .filter(measurement.date >= start_date)\
            .filter(measurement.date <= end_date).all()
        
        session.close()
        
        tobs_list = list(np.ravel(results))
    
        # convert to a json and display.
        return jsonify(tobs_list)

## app launcher
if __name__ == "__main__":
    app.run(debug=True)
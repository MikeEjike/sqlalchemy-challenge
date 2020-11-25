import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measure = Base.classes.measurement
stat = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/2016-08-23/2017-08-23<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_year_dates = session.query(measure.date).filter(measure.date <= '2017-08-23', measure.date >= '2016-08-23').order_by(measure.date).all()

   # Perform a query to retrieve the data and precipitation scores
    dates_prcp = session.query(measure.date, measure.prcp).filter(measure.date <= '2017-08-23', measure.date >= '2016-08-23').order_by(measure.date).all()

    session.close()

    # Dict with date as the key and prcp as the value
    ppp = {date: prcp for date, prcp in dates_prcp}
    return jsonify(ppp)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)


    station_data = session.query(stat.station).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    station_list = list(np.ravel(station_data))
    return jsonify(station_list=station_list)


@app.route("/api/v1.0/tobs")
def temp_monthly():

    session = Session(engine)


    # Calculate the date 1 year ago from last date in database
    high_stat_last_year_dates = session.query(measure.date).filter(measure.station == 'USC00519281').filter(measure.date <= '2017-08-23', measure.date >= '2016-08-23').order_by(measure.date).all()

    # Query the primary station for all tobs from the last year
    high_stat_dates_tobs = session.query(measure.date, measure.tobs).filter(measure.station == 'USC00519281').filter(measure.date <= '2017-08-23', measure.date >= '2016-08-23').order_by(measure.date).all()

    session.close()

    temps_list = list(np.ravel(high_stat_dates_tobs))

    return jsonify(temps_list=temps_list)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Select statement
    
    
    session = Session(engine)

    desc = [func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs)]

    if not end:


        # calculate TMIN, TAVG, TMAX for dates greater than start
        data = session.query(*desc).filter(measure.date >= start).all()
        

        # Unravel results into a 1D array and convert to a list
        temp = list(np.ravel(data))
        return jsonify(temp)


    # calculate TMIN, TAVG, TMAX with start and stop
    data = session.query(*desc).filter(measure.date >= start).filter(measure.date <= end).all()
    
    session.close()

    temp = list(np.ravel(data))
    return jsonify(temp=temp)


if __name__ == '__main__':
    app.run()

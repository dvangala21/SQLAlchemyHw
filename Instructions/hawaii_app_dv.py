import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Variable Setup
date_start_query = '2016-08-23'
latest = '2017-08-23'

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Route /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """
    Convert the query results to a Dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary.
    """
    
    results = session.query(Measurement.date, func.avg(Measurement.prcp)).filter(Measurement.date>=date_start_query).group_by(Measurement.date).all()

    results_list = []
    for date, prcp in results:
        results_list.append({str(date): prcp})
    return jsonify(results_list)


@app.route("/api/v1.0/stations")
def stations(): 
    """
    Return a JSON list of stations from the dataset
    """

    results = session.query(Station.station).all()
    results_list = list(np.ravel(results))

    return jsonify(results_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """
    query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year.
    """
    results = session.query(Measurement.date, func.avg(Measurement.tobs)). \
                filter(Measurement.date>=date_start_query). \
                group_by(Measurement.date).all()

    results_list = []
    for date, temp in results:
        results_list.append({str(date): temp})
    return jsonify(results_list)

#BROKEN
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=latest):

    '''
    Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    '''

    start_date_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    if end == latest:
        end_date_dt = end
    else:
        end_date_dt = dt.datetime.strptime(end, '%Y-%m-%d')

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temps = session.query(*sel). \
                filter(Measurement.date>=start_date_dt). \
                filter(Measurement.date<=end_date_dt).all()[0]
    
    results_list = [{"temp_min": temps[0]}, 
                    {"temp_avg": temps[1]}, 
                    {"temp_max": temps[2]}]
    return jsonify(results_list)

if __name__ == '__main__':
    app.run(debug=True)

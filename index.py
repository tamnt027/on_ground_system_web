

import datetime
from http.client import responses
from init import app, login
from flask_login import login_user
from flask import render_template, request, redirect, jsonify
from admin import *
from models import Sensor
import utils
from influxdb_helper import InfluxDbHelper
from process import IrrigationProcess
@app.route("/")
def home():
    charts = utils.get_active_charts()
    return render_template( "index.html", charts=charts)


@app.route("/admin-login", methods=['post'] )
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = utils.check_login(username=username, password=password)
    if user:
        login_user(user=user)
    
    return redirect("/admin")

# @app.route("/irrigation")
# def irrigation():

#     irrigation_process = IrrigationProcess(None)
#     irrigation_process.start()

#     return render_template( "index.html")

# http://127.0.0.1:5000/api/sensors/1/data
@app.route("/api/sensors/<int:sensor_id>/data")
def sensor_info(sensor_id):
    sensor = utils.get_sensors(sensor_id=sensor_id)
    if sensor is None:
        return { "status" : "fail",
                 "message" : f"Sensor id {sensor_id} not exist."}

    
    # time_range = request.form.get("time_range")
    time_range = request.args.get('timerange')
    
    if time_range is None:
        time_range = '2h'
    
    measurement = sensor.lora.measurement
    dev_eui = sensor.lora.device_id
    period = request.args.get('period')
    if period is None:
        period = '1m'
    
    influxdb_helper = InfluxDbHelper.get_instance()
    timestamps, values = influxdb_helper.get_sensor_data(time_range=time_range, 
                                    measurement=measurement, period=period, dev_eui=dev_eui)
    
    response = {
                "status" : "success",
                "id": sensor_id, 
                "name": sensor.name,
                "measurement" : sensor.lora.measurement,
                "timestamps" : timestamps, 
                "values" : values}
    return jsonify(response)


def get_sensor_data(sensor : Sensor, timerange, period):
    measurement = sensor.lora.measurement
    dev_eui = sensor.lora.device_id
    
    influxdb_helper = InfluxDbHelper.get_instance()
    timestamps, values = influxdb_helper.get_sensor_data(time_range=timerange, 
                                    measurement=measurement, period=period, dev_eui=dev_eui)
    return timestamps, values


@app.route("/api/charts/<int:chart_id>/data")
def get_chart_data(chart_id):
    chart = utils.get_chart(chart_id)
    if chart is None or chart.active == False:
        return { "status" : "fail",
                 "message" : f"Chart id {chart_id} not exist."} 
    
    try:
        sensor = chart.sensor
        secondary_sensor = chart.secondary_sensor
        
        timerange = request.args.get('timerange')
        if timerange is None:
            timerange = chart.timerange
            
        period = request.args.get('period')
        if period is None:
            period = chart.period

        timestamps, values = get_sensor_data(sensor=sensor, timerange=timerange, period=period)
        
        response = {
                    "status" : "success",
                    "id": chart.id, 
                    "sensor" : {
                        "timestamps" : timestamps,
                        "values" : values
                        },
                    "secondary" : "false",
                    
                }
                
        if secondary_sensor is not None:
            timestamps_secondary, values_secondary = get_sensor_data(sensor=secondary_sensor, timerange=timerange, period=period)

            response["secondary"] = "true"
            response["secondary_sensor"] = {
                        "timestamps" : timestamps_secondary,
                        "values" : values_secondary
                        }
    except:
        response = { "status" : "fail",
                     "message" : f"Unexpected error when get sensor data"} 

    
    return jsonify(response)

@app.route("/api/charts/<int:chart_id>")
def get_chart(chart_id):
    chart = utils.get_chart(chart_id)
    if chart is None or chart.active == False:
        return { "status" : "fail",
                 "message" : f"Chart id {chart_id} not exist."} 
    
    response = {
                "status" : "success",
                "id": chart.id, 
                "title": chart.title,
                "background_color0" : chart.background_color0.value,
                "background_color1" : chart.background_color1.value,
                "secondary" : "false",
                "sensor" : {
                    "id": chart.sensor.id,
                    "name" : chart.sensor.name,
                    },
              }
    if chart.secondary_sensor is not None:
        response["secondary"] = "true"
        response["secondary_sensor"] = {
            "id": chart.secondary_sensor.id,
            "name" : chart.secondary_sensor.name
        }
    
    return jsonify(response)



@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id)

@app.route("/<string:name>")
def hello(name):
    return f"<h1>Hello , {name} </h1>"


if __name__ == '__main__':
    app.run(debug=True)
import os
import pymysql
from http import HTTPStatus
from flask_cors import CORS
from flask import Flask, jsonify, redirect, request, jsonify, url_for, abort, render_template
from db import Database
from config import DevelopmentConfig as devconf
from flaskext.mysql import MySQL

import boto3
import requests

host = os.environ.get('FLASK_SERVER_HOST', devconf.HOST)
port = os.environ.get('FLASK_SERVER_PORT', devconf.PORT)
version = str(devconf.VERSION).lower()
url_prefix = str(devconf.URL_PREFIX).lower()
route_prefix = f"/{url_prefix}/{version}"

def create_app():
    app = Flask(__name__,template_folder='template')
    cors = CORS(app, resources={f"{route_prefix}/*": {"origins": "*"}})
    app.config.from_object(devconf)
    return app

def get_response_msg(data, status_code):
    message = {
        'status': status_code,
        'data': data if data else 'No records found'
    }
    response_msg = jsonify(message)
    response_msg.status_code = status_code
    return response_msg


app = create_app()
wsgi_app = app.wsgi_app
db = Database(devconf)

## ==============================================[ Routes - Start ]

## /api/v1/getcity?country=IND
@app.route(f"{route_prefix}/getcity", methods=['GET'])
def getdata():
    try:
        countrycode = request.args.get('country', default='IND', type=str)
        query = f"SELECT id,name,countrycode FROM appdb.Country WHERE COUNTRYCODE='{countrycode.upper()}'"
        records = db.run_query(query=query)
        response = get_response_msg(records, HTTPStatus.OK)
        db.close_connection()

        countrylist = [{"id": item[0], "name": item[1] , "country": item[2] } for item in records]
        response = jsonify(countrylist)
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


@app.route("/home", methods=['GET','POST'])
def  home():  
        
    BUCKET_NAME = "country-flag-image-bucket"
    s3 = boto3.client('s3', aws_access_key_id='AKIA5QL5DXKIJE2GHW5F', aws_secret_access_key='')
    buckets_response = s3.list_buckets()

    #for bucket in buckets_response["Buckets"]:
                #print(bucket)
    images = list()

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    counter = 0
    for obj in response["Contents"]: 
        #print(counter)
        if counter > 0:
            url = s3.generate_presigned_url(
            "get_object", 
            Params={"Bucket":BUCKET_NAME,  "Key": obj['Key']}, 
            ExpiresIn=30)
            images.append(url)
        counter +=1

    # The API endpoint
    #api_endpoint = f"http://{host}:{port}/api/v1/getcity?country=GBR"
    api_endpoint = "http://api.midax.co.uk/api/v1/getcity?country=GBR"
    # A GET request to the API
    response = requests.get(api_endpoint)
    country_data = response.json()

    return render_template('home.html',imagelist=images, countries=country_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'POST':    
    #     # Perform login authentication
    #     username, password = ""
    #     username = request.form['username']
    #     password = request.form['password']

    # Add your authentication logic here
    # if username == 'admin' and password == 'password':
    #     return 'Login successful!'
    # else:
    #     return "Invalid username or password"

    # If the request method is GET, render the login template
    return render_template('login.html')



## /api/v1/getcitycodes
@app.route(f"{route_prefix}/getcitycodes", methods=['GET'])
def getcitycodes():
    try:
        query = f"SELECT distinct(COUNTRYCODE) FROM appdb.city"
        records = db.run_query(query=query)

        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


## /api/v1/health
@app.route(f"{route_prefix}/health", methods=['GET'])
def health():
    try:
        db_status = "Connected to DB" if db.db_connection_status else "Not connected to DB"
        response = get_response_msg("I am fine! " + db_status, HTTPStatus.OK)       
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

## /
@app.route('/', methods=['GET'])
def default():
    return redirect(url_for('health'))

## =================================================[ Routes - End ]

## ================================[ Error Handler Defined - Start ]
## HTTP 404 error handler
@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(e):    
    return get_response_msg(data=str(e), status_code=HTTPStatus.NOT_FOUND)


## HTTP 400 error handler
@app.errorhandler(HTTPStatus.BAD_REQUEST)
def bad_request(e):
    return get_response_msg(str(e), HTTPStatus.BAD_REQUEST)


## HTTP 500 error handler
@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_server_error(e):
    return get_response_msg(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
## ==================================[ Error Handler Defined - End ]

app.run(debug=True)

if __name__ == '__main__':
    ## Launch the application 
    app.run(host=host, port=port)
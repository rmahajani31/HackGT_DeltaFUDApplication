import urllib2
import MySQLdb
import json
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant

host = "localhost"
server_user = "root"
server_password = "hackgt2016"
database = "user_accounts"

db = MySQLdb.connect(host, server_user, server_password, database)
cursor = db.cursor()

def get_coords(flight_number, flight_origin_date):
    api_call = ''.join(["https://demo30-test.apigee.net/v1/hack/status"
                        "?flightNumber=", str(flight_number),"&flightOriginDate=",
                        flight_origin_date,
                        "&apikey=ZINxBqol4GEAB9L1T25ZcFyG9vmapoLW"])
    new_flight_info = urllib2.urlopen(api_call).read()
    flight_info_json = json.loads(new_flight_info)
    arrivalLat = flight_info_json["flightStatusResponse"]["statusResponse"][
    "flightStatusTO"]["flightStatusLegTOList"]["arrivalTsoagLatitudeDecimal"]
    arrivalLong = flight_info_json["flightStatusResponse"]["statusResponse"][
        "flightStatusTO"]["flightStatusLegTOList"]["arrivalTsoagLongitudeDecimal"]
    return [arrivalLat, arrivalLong]


def call_uber(flight_number, flight_origin_date):
    coords = get_coords(flight_number, flight_origin_date)
    server_token = "GSYPRMkSl_a7qQn8FH6d4imBjBnvrTWhh-6OzVPX"
    session = Session(server_token)
    client = UberRidesClient(session)
    response = client.get_products(coords[0], coords[1])
    products = response.json.get('products')
    auth_flow = AuthorizationCodeGrant(
        "gT2GLeVlXMQkrWWBO872bcjHK168Tr8W",
        None,
        "fQMuhWzwuvMiy2yl31qDu4xIRMP0DIVQQUtJy3hj",
        None,
    )
    auth_url = auth_flow.get_authorization_url()
    session = auth_flow.get_session()
    client = UberRidesClient(session, sandbox_mode=True)
    credentials = session.oauth2credential
    get_coords()
    response = client.request_ride(
        start_latitude=coords[0],
        start_longitude=coords[1],
    )
    ride_details = response.json
    ride_id = ride_details.get('request_id')


def verify_flight():
    sql = "select FlightNumber, Date " \
          "from users" \
          "where UserName = user"
    cursor.execute(sql)
    results = cursor.fetchall()
    flight_number = results[0][0]
    flight_origin_date = results[0][1]
    api_call = ''.join(["https://demo30-test.apigee.net/v1/hack/status"
                        "?flightNumber=", str(flight_number),"&flightOriginDate=",
                        flight_origin_date,
                        "&apikey=ZINxBqol4GEAB9L1T25ZcFyG9vmapoLW"])
    new_flight_info = urllib2.urlopen(api_call).read()
    flight_info_json = json.loads(new_flight_info)
    actual_flight = flight_info_json["flightStatusResponse"]["status"]
    if actual_flight == "SUCCESS":
        return True
    else:
        return False

# verify_flight(input_flight_number, input_flight_origin_date)

from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import json
from  prettytable import PrettyTable
load_dotenv()



app = Flask(__name__)

@app.route('/')
def status_check():
    print("hello")
    return jsonify({"message": "welcome"})


BLS_API_KEY = os.getenv('BLS_API_KEY')
def fetch_bls_data(series_id_list, startyear, endyear):
    # we want career outlook information, salary information, education level, job locations, skills
    BLS_ENDPOINT = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
    headers = {'Content-type': 'application/json'}

    data = json.dumps({
        'seriesid': series_id_list,
        'registrationkey': BLS_API_KEY,
        'startyear' : startyear,
        'endyear' : endyear,
        })


    response = requests.post(BLS_ENDPOINT, data=data, headers=headers)
    result = json.loads(response.text)
    print(result)
    table = PrettyTable(["series id","year","period","period name", "value"])
    for series in result['Results']['series']:
        series_id = series['seriesID']
        for data_p in series['data']:
            year = data_p['year']
            period = data_p['period']
            period_name = data_p['periodName']
            value = data_p['value']

            table.add_row([series_id, year, period, period_name, value])

    print(table)
    return result

series_id_list = ['OEUN000000000000015125213', 'OEUN000000000000015125201']
if __name__ == "__main__":
        fetch_bls_data(series_id_list, '2024', '2024')
#OEUN000000000000015125213
#OEUN000000000000015125201
from flask import Flask
from github import Github
import requests
import json
import os
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/', )
def hello_world():
    return 'Welcome API!'


# find all defi amount in geojson file
def find_defi(json_obj, name):
    amount = 0
    for dict in json_obj:
        if dict['type'] == name:
            amount += 1
    return amount


# find all 24/7 opening hours amount in geojson file
def find_hours(json_obj, name):
    amount = 0
    for dict in json_obj:
        if "opening_hours" not in dict["properties"]:
            continue
        else:
            if dict["properties"]["opening_hours"] == name:
                amount += 1
    return amount


# get pie chart data in geojson file
def piechart_data():
    with open("defis_switzerland.geojson", "r") as read_file:
        data = json.load(read_file)
    json_obj = data["features"]
    pie_data = {}
    amount = len(json_obj)
    unknown_amount = 0
    opening_only = 0
    opening_24 = 0
    for dict in json_obj:
        if "opening_hours" not in dict["properties"]:
            unknown_amount += 1
        else:
            if dict["properties"]["opening_hours"] == "24/7":
                opening_24 += 1
            else:
                opening_only += 1
    pie_data["all"] = amount
    pie_data["unknown"] = unknown_amount
    pie_data["open_only"] = opening_only
    pie_data["open_24"] = opening_24

    return pie_data


# get defi counts each geojson file (include "defis_kt" string)
def barchart_data():
    current_path = os.path.join(os.path.abspath(os.getcwd()), "json")
    keyword = 'defis_kt'
    result = {}
    label = []
    bar_data = []
    for file in os.listdir(current_path):
        if keyword in file:
            each_file = os.path.join(current_path, file)
            with open(each_file, "r") as read_file:
                data = json.load(read_file)
            each_defi = find_defi(data["features"], "Feature")
            label.append(file.replace("defis_kt_", "").replace(".geojson", ""))
            bar_data.append(each_defi)
    result["label"] = label
    result["data"] = bar_data
    return result


# get file name counts that include "dispo" string
def find_dispo():
    current_path = os.path.join(os.path.abspath(os.getcwd()), "json")
    keyword = 'dispo'
    result = 0
    for file in os.listdir(current_path):
        if keyword in file:
            result += 1
    return result


# app route api get method make data
@app.route('/api', methods=['GET'])
def fetch_json():
    result_data = {}
    # fetch json
    # username = "artsiomliaver"
    # token = "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"
    # github_session = requests.Session()
    # github_session.auth = (username, token)

    # json_url = "https://github.com/chnuessli/defi_data/blob/main/data/json/defis_switzerland.geojson"
    #
    # g = Github("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")
    # # for repo in g.get_user().get_repos():
    # #     print(repo.name)
    # repo = g.get_repo("chnuessli/defi_stats")
    # contents = repo.get_contents("app/frontend")
    # for content_file in contents:
    #     print(content_file)
    with open("defis_switzerland.geojson", "r") as read_file:
        data = json.load(read_file)

    all_defi = find_defi(data["features"], "Feature")
    result_data["all"] = all_defi

    all_hours = find_hours(data["features"], "24/7")
    result_data["hours"] = all_hours

    dispo_data = find_dispo()
    result_data["dispo"] = dispo_data

    bar_data = barchart_data()
    result_data["bar_data"] = bar_data

    pie_data = piechart_data()
    result_data["pie_data"] = pie_data

    return_data = jsonify(result_data)
    return return_data


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")

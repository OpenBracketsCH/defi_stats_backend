from flask import Flask
from github import Github
import requests
import json
import os
from flask import jsonify
from flask_cors import CORS
import base64
import sqlite3

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
    g = Github("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")
    repo = g.get_repo("chnuessli/defi_data")

    try:
        file_content = repo.get_contents("data/json/defis_switzerland.geojson", ref="sha")
        data = json.loads(file_content.decoded_content.decode())
    except:
        file_content = get_blob_content(repo, "main", "data/json/defis_switzerland.geojson")
        data = json.loads(base64.b64decode(file_content.content))
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
    with open('match.json', encoding="utf8") as f:
        match_data = json.load(f)

    g = Github("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")
    repo = g.get_repo("chnuessli/defi_data")
    contents = repo.get_contents("data/json")
    keyword = 'defis_kt'
    result = {}
    label = []
    bar_data = []
    for content_file in contents:
        if keyword in content_file.name:
            try:
                file_content = repo.get_contents(content_file.path)
                data = json.loads(file_content.decoded_content.decode())
            except:
                file_content = get_blob_content(repo, "main", content_file.path)
                data = json.loads(base64.b64decode(file_content.content))

            each_defi = find_defi(data["features"], "Feature")
            match_name = content_file.name.replace("defis_kt_", "").replace(".geojson", "")
            if match_name not in match_data:
                label.append(match_name)
            else:
                label.append(match_data[match_name])
            bar_data.append(each_defi)
    result["label"] = label
    result["data"] = bar_data
    return result


# get line chart data
def linechart_data():
    result = {}
    label = []
    data = []
    con = sqlite3.connect('defi_data.db')
    cur = con.cursor()

    # Insert a row of data
    cur.execute("""SELECT * FROM (
                   SELECT * FROM defi_data ORDER BY id DESC LIMIT 7
                )Var1
                   ORDER BY id ASC;""")

    rows = cur.fetchall()
    for row in rows:
        label.append(row[2])
        data.append(row[1])
    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

    result["label"] = label
    result["data"] = data
    return result


# get file name counts that include "dispo" string
def find_dispo():
    g = Github("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")
    repo = g.get_repo("chnuessli/defi_data")
    contents = repo.get_contents("data/json")
    keyword = 'dispo'
    result = 0
    for content_file in contents:
        if keyword in content_file.name:
            result += 1
    return result


def get_blob_content(repo, branch, path_name):
    # first get the branch reference
    ref = repo.get_git_ref(f'heads/{branch}')
    # then get the tree
    tree = repo.get_git_tree(ref.object.sha, recursive='/' in path_name).tree
    # look for path in tree
    sha = [x.sha for x in tree if x.path == path_name]
    if not sha:
        # well, not found..
        return None
    # we have sha
    return repo.get_git_blob(sha[0])


# app route api get method make data
@app.route('/api', methods=['GET'])
def fetch_json():
    result_data = {}
    g = Github("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")
    repo = g.get_repo("chnuessli/defi_data")
    try:
        file_content = repo.get_contents("data/json/defis_switzerland.geojson", ref="sha")
        data = json.loads(file_content.decoded_content.decode())
    except:
        file_content = get_blob_content(repo, "main", "data/json/defis_switzerland.geojson")
        data = json.loads(base64.b64decode(file_content.content))

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

    line_data = linechart_data()
    result_data["line_data"] = line_data

    return_data = jsonify(result_data)
    return return_data


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")

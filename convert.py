import json
import sys
import os
import difflib

def get_names_from_json():
    names = []

    with open("config/input_registers.json") as f:
        conf = json.load(f)
        names.extend([n["name"] for n in conf["registers"]])

    with open("config/meter_input.json") as f:
        conf = json.load(f)
        names.extend([n["name"] for n in conf["registers"]])
    return names

FIELDS_NAMES = get_names_from_json()

def get_closest_name(name):
    match = difflib.get_close_matches(name, FIELDS_NAMES, 1)
    return match

def convert_target(target):
    n_target = {}
    n_target["datasource"] = {
        "type": "influxdb",
        "uid": "{{ influxdb_datasource_uid }}",
    }

    field = target["expr"].split("{")[0]
    
    field_name = get_closest_name(field)

    if field_name is None:
        print("Field not found")
        exit()

    n_target["query"] = f"""
        from(bucket: \"DHBW\")
            |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
            |> filter(fn: (r) => r[\"_field\"] == \"{field_name[0]}\")
            |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
            |> yield(name: \"last\")
    """

    return n_target

def convert_targets(targets):
    for i, target in enumerate(targets):
        targets[i] = convert_target(target.copy())

    return targets

def get_dict_from_string(inp):
    out = {}
    for f in inp.strip("{}").split(","):
        name, value = f.split("=")
        value = value.strip("\"")
        out[name] = value
    return out

def convert_trans_fields(fields):
    n_fields = {}
    for f in fields:
        if f.startswith("{__name__"):
            rec = get_dict_from_string(f)
            name = get_closest_name(rec["__name__"])[0]
            n_fields[name] = fields[f]
        else:
            n_fields[f] = fields[f]
    return n_fields
    
def convert_trans_options(opt):
    opt["fields"] = convert_trans_fields(opt["fields"].copy())
    return opt
    
def convert_transformation(trans):
    if trans["id"] != "groupBy":
        return trans
    trans["options"] = convert_trans_options(trans["options"].copy())

    return trans

def convert_transformations(transformations):
    for i, trans in enumerate(transformations):
        transformations[i] = convert_transformation(trans.copy())

    return transformations

def convert_panel(panel):
    panel["datasource"] = {
        "type": "influxdb",
        "uid": "influxdbsource",
    }

    panel["targets"] = convert_targets(panel["targets"].copy())
    if "transformations" in panel:
        panel["transformations"] = convert_transformations(panel["transformations"].copy())

    return panel

def convert_panels(panels):
    for i, panel in enumerate(panels):
        panels[i] = convert_panel(panel.copy())
    return panels

def convert(dash):
    n_dash = dash["dashboard"]
    n_dash["uid"] = n_dash["title"].lower().replace(" ", "_").ljust(14, "0")
    n_dash["panels"] = convert_panels(dash["dashboard"]["panels"].copy())
    return n_dash

for file in os.listdir("prometheus"):
    print(f"converting {file}")
    with open("prometheus/"+file) as f:
        dash = json.load(f)
        res = convert(dash)
        with open("influx/"+file+".j2", "w") as out:
            json.dump(res, out)

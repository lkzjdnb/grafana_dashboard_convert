# Takes a filename as input, converts it from prometheus to grafana
# Return the output to the second input

import json
import sys

def convert_target(target):
    n_target = {}
    n_target["datasource"] = {
        "type": "influxdb",
        "uid": "influxdbsource",
    }

    field = target["expr"].split("{")[0]

    n_target["query"] = f"""
        from(bucket: \"DHBW\")
            |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
            |> filter(fn: (r) => r[\"_measurement\"] == "electrolyzer\")
            |> filter(fn: (r) => r[\"_field\"] == \"{field}\")
            |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)
            |> yield(name: \"last\")
    """

    return n_target

def convert_targets(targets):
    for i, target in enumerate(targets):
        targets[i] = convert_target(target.copy())

    return targets

def convert_panel(panel):
    panel["datasource"] = {
        "type": "influxdb",
        "uid": "influxdbsource",
    }

    panel["targets"] = convert_targets(panel["targets"].copy())

    return panel

def convert_panels(panels):
    for i, panel in enumerate(panels):
        panels[i] = convert_panel(panel.copy())
    return panels

def convert(dash):
    n_dash = dash["dashboard"]
    n_dash["panels"] = convert_panels(dash["dashboard"]["panels"].copy())
    return n_dash

with open(sys.argv[1]) as f:
    dash = json.load(f)
    res = convert(dash)
    with open(sys.argv[2], "w") as out:
        json.dump(res, out)

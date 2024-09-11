# Grafana dashboard convert
Simple scripts to download dashboards and convert them from Prometheus request to Flux (InfluxDB).

## Usage
### Download
`python dowload_all.py`

Will update the dashboards in [prometheus/](/prometheus) with the lastest version found on the server.

### Convert
`python convert.py`

Will convert all the dashboards in [prometheus/](/prometheus) to InfluxDB and save them in [influx/](/influx).
Note that exported dashboards are in the .j2 ([Jinja](https://jinja.palletsprojects.com/en/3.1.x/)) to allow for templating the datasource uid on install.

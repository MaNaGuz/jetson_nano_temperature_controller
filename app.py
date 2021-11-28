import re
import os
import json

from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/temperature", methods=['GET'])
def temperature():

    def generator():
        while True:
            path = "/sys/devices/virtual/thermal"
            dir_list = os.listdir(path)
            thermal_zones = [x for x in dir_list if re.search('^thermal_zone\\d$', x)]
            thermal_data = {}
            
            for thermal_zone in thermal_zones:
                with open('%s/%s/type' % (path, thermal_zone), 'r') as type_file:
                    device_type = type_file.read().strip()
            
                with open('%s/%s/temp' % (path, thermal_zone), 'r') as temp_file:
                    device_temp = temp_file.read()
                thermal_data[device_type] = device_temp.strip()

            yield json.dumps(thermal_data)

    return Response(generator(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)

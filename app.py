import re
import os
import json

from flask import Flask, render_template, Response

stream = os.popen("hostname -I")
ips = stream.read().strip().split(" ")
host_ip = None
for ip in ips:
    if re.search(r'^192\.168\.1\.[0-9]{1,3}$', ip):
        host_ip = ip
        break

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html", host_ip=host_ip)

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
                thermal_data[device_type] = int(device_temp.strip())/1000

            yield f'data: {json.dumps(thermal_data)}\n\n'

    return Response(generator(), mimetype='text/event-stream')

if __name__ == "__main__":
    if not host_ip:
        raise RuntimeError('Server ip was not detected')
    app.run(host="0.0.0.0", port="5000", debug=True)

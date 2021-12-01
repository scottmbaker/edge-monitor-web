from bottle import route, run, static_file, request, subprocess
from ipaddress import ip_address
import re

def validateHostName(s):
    try:
        ip_address(s)
        return True
    except ValueError:
        disallowed = re.compile("[^a-zA-Z\d\-]")
        return all(map(lambda x: len(x) and not disallowed.search(x), s.split(".")))

@route("/")
def index():
    return static_file("index.html", root=".")

@route("/webui.js")
def webui_js():
    return static_file("webui.js", root=".")

@route("/ping")
def ping():
    ip = request.query.ip or "127.0.0.1"
    if not validateHostName(ip):
        return {"stdout": "", "stderr": "invalid hostname or ip_address", "returncode": -2}

    ping = subprocess.Popen(["ping", "-n", "-c", "1", "-w", "1", ip],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = ping.communicate()
    if ping.returncode != 0:
        return {"stdout": stdout, "stderr": stderr, "returncode": ping.returncode}
    else:
        lines = stdout.splitlines()
        for line in lines:
            line = line.decode("utf-8") 
            if "bytes from" in line:
                return {"stdout": stdout, "stderr": stderr, "returncode": ping.returncode, "result": line}

    # It was a successful response, but without a "bytes from" line. Should not happen.
    return {"stdout": stdout, "stderr": stderr, "returncode": -1}


run(host='0.0.0.0', port=8087, debug=True)
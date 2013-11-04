from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import cgi
import urlparse
import sqlite3
import datetime
import json
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-p","--port", dest="port", action="store", type="int",
                  help="start server on PORT", metavar="PORT", default=9999)
(options, args) = parser.parse_args()

PORT_NUMBER = options.port

DROP_TABLE = "DROP TABLE IF EXISTS records"

CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS records (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_type TEXT,
    record_value INTEGER,
    log_datetime TEXT
)'''

LOG_TEMPERATURE = '''
INSERT INTO 
records(record_type, record_value, log_datetime)
VALUES ( "temperature", ?, ?)
'''

LOG_HUMIDITY = '''
INSERT INTO
records(record_type, record_value, log_datetime)
VALUES ( "humidity", ?, ?)
'''

GET_RECORDS = '''
SELECT * FROM records
WHERE record_type=?
ORDER BY log_datetime DESC LIMIT ? 
'''

GET_TODAY = '''
SELECT * FROM records
WHERE record_type=? 
AND date(log_datetime,"start of day") == date("now", "start of day")
ORDER BY log_datetime DESC
'''

GET_ALL = '''
SELECT * FROM records
WHERE record_type=? 
ORDER BY log_datetime DESC
'''

def connect():
    return sqlite3.connect("temperature.db")

def init_db(drop = False):
    conn = connect()
    try:
        c = conn.cursor()
        if drop:
            c.execute(DROP_TABLE)

        c.execute(CREATE_TABLE)
        conn.commit()
    finally:
        conn.close()

def log_temperature(temp):
    conn = connect()
    try:
        c = conn.cursor()
        c.execute(LOG_TEMPERATURE,
                [ int(temp * 10), datetime.datetime.now().isoformat() ])
        conn.commit()
    finally:
        conn.close()

def log_humidity(humid):
    conn = connect()
    try:
        c = conn.cursor()
        c.execute(LOG_HUMIDITY,
                [ humid, datetime.datetime.now().isoformat() ])
        conn.commit()
    finally:
        conn.close()

def get_records(count):
    conn = connect()
    (temperatures, humidities) = (None, None)
    try:
        c = conn.cursor()
        c.execute(GET_RECORDS, [ "temperature", count ])
        temperatures = c.fetchall()
        c.execute(GET_RECORDS, [ "humidity", count ])
        humidities = c.fetchall()
    finally:
        conn.close()

    return (temperatures, humidities)

def get_today():
    conn = connect()
    (temperatures, humidities) = (None, None)
    try:
        c = conn.cursor()
        c.execute(GET_TODAY, [ "temperature" ])
        temperatures = c.fetchall()
        c.execute(GET_TODAY, [ "humidity" ])
        humidities = c.fetchall()
    finally:
        conn.close()

    return (temperatures, humidities)

def get_all():
    conn = connect()
    (temperatures, humidities) = (None, None)
    try:
        c = conn.cursor()
        c.execute(GET_ALL, [ "temperature" ])
        temperatures = c.fetchall()
        c.execute(GET_ALL, [ "humidity" ])
        humidities = c.fetchall()
    finally:
        conn.close()

    return (temperatures, humidities)

def dt(iso):
    return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%f")

def json_for(records):
    (temperatures, humidities) = records
    temps = [ { "temperature" : float(r[2]) / 10,
                "when" : r[3] } for r in temperatures ]

    humids = [ { "humidity" : int(r[2]),
                "when" : r[3] } for r in humidities ]

    records = { "temperatures": temps, "humidities" : humids }
    return json.dumps(records)

class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print self.path
            parsed = urlparse.urlparse(self.path)
            if parsed.path == "/last":
                try:
                    records = get_records(int(parsed.query))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json_for( records ))
                except:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write("Invalid query string")

            elif parsed.path == "/today":
                records = get_today()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json_for( records ))

            elif parsed.path == "/all":
                records = get_all()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json_for( records ))

            elif parsed.path == "/graph":
                self.send_response(200)
                self.end_headers()
                with open("prettyGraph.html") as f:
                    self.wfile.write(f.read())

            else:
                self.send_error(404,'File Not Found: %s' % self.path)

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):

        (host,port) = self.client_address
        if host != "imp.electricimp.com" and host != "184.169.136.13":
            print "Denied to", host
            self.send_response(403)
            self.end_headers()
            self.wfile.write("Permission denied: " +host)
            return
        
        if self.path=="/submit":
            length = int(self.headers['Content-Length'])
            post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))

            if post_data.has_key("temperature"):
                log_temperature(float(post_data["temperature"][0]))

            if post_data.has_key("humidity"):
                log_humidity(int(post_data["humidity"][0]))

            self.send_response(200)
            self.end_headers()
            self.wfile.write("OK")
            return
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Not found")

try:
    init_db(False)

    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started on port ' , PORT_NUMBER
    server.serve_forever()

except KeyboardInterrupt:
    server.socket.close()


from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import urlparse
import sqlite3
import datetime

PORT_NUMBER = 9999

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

class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.end_headers()
            self.wfile.write("OK")

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):
        
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
    init_db(True)

    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started on port ' , PORT_NUMBER
    server.serve_forever()

except KeyboardInterrupt:
    server.socket.close()


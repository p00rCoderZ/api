from sanic import Sanic
import toml

app = Sanic()
DBNAME = app.config['DBNAME'] if "DBNAME" in app.config else 'kup'
SERIAL = 'serial' if "DBNAME" in app.config else toml.load('/secrets.toml')['serial']
DSN = 'postgres://pros:foobar@postgres:5432/{}'.format(DBNAME)
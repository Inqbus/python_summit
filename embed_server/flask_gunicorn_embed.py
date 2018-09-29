# Asyncio wird benötigt um in python IO zu parallelisieren 
try:
    import asyncio
except ImportError:
    raise RuntimeError("This example requries Python3 / asyncio")

# Bokeh Abhängigkeiten
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import server_document
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
from bokeh.server.util import bind_sockets
from bokeh.themes import Theme

# Numercal Python importieren
import numpy as np

# Tornado webserver
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

# Flask Webframework
from flask import Flask, render_template

# Welcome message
if __name__ == '__main__':
    print('This script is intended to be run with gunicorn. e.g.')
    print()
    print('    gunicorn -w 4 flask_gunicorn_embed:app')
    print()
    print('will start the app on four processes')
    import sys
    sys.exit()

# Flask starten
app = Flask(__name__)

# Bokeh Code der Applikation 
def modify_doc(doc):

    # Konstante für maximale X-Ausdehnung
    N = 100
    X_MAX = 4*np.pi
    k = 1

    # Definiere Initiale Daten
    x = np.linspace(0, X_MAX, N)
    y = np.sin(k*x)

    # Definiere eine Datenquelle
    source = ColumnDataSource(data=dict(x=x, y=y))

    # Ein Plot-Objekt wird definiert
    plot = figure()
    # welches einen Linien-Plot beinhaltet 
    plot.line('x', 'y', source=source)

    # Ein Schieberegler wird definiert
    freq = Slider(title="freq", value=1.0, start=1, end=105, step=0.1)

    # Diese Funktion soll gerufen werden, wenn der Schieberegler sich ändert ..
    def update_data(attrname, old, new):
        k = freq.value
        x = np.linspace(0, X_MAX, N)
        y = np.sin(k*x)
        source.data =dict(x=x, y=y)
        
    # .. was hier verdrahtet wird
    freq.on_change('value', update_data)
                    
    # Hier wird eine Box im Browser erzeut, welche den Schieberegler enthält
    inputs = widgetbox(freq)
                    
    # Diese Box wir im HTML-Document mit dem Plot in einer Zeile ausgerichtet
    doc.add_root(row(inputs, plot, width=800))
    
#    doc.theme = Theme(filename="theme.yaml")

# Die Bokeh Applikations-Instanz
# can't use shortcuts here, since we are passing to low level BokehTornado
bkapp = Application(FunctionHandler(modify_doc))

# Hier wird jedem gunicorn Unterprozess ein anderer Port/Websocket-Port zugewiesen
# This is so that if this app is run using something like "gunicorn -w 4" then
# each process will listen on its own port
sockets, port = bind_sockets("localhost", 0)
print(sockets)

# Die Main-site
@app.route('/', methods=['GET'])
def bkapp_page():
    # Hier wird der Bokeh-Server gestartet
    script = server_document('http://localhost:%d/bkapp' % port)
    # und dem Flask Template zum einbetten übergeben 
    return render_template("embed.html", script=script, template="Flask")

# Dies erzeugt einen Gunicorn worker thread, der jeweils eine Tornado Instanz ist. Flask kann keine Websockets, daher wird Tornado benötigt.
def bk_worker():
    asyncio.set_event_loop(asyncio.new_event_loop())

    # Die Bokeh Tornado Instanz. Wichtig ist hier unter "extra_websocket_origins" den Flask-Sever IP:Port anzugeben, sonst nimmt Tornado den Websocket nicht an  
    bokeh_tornado = BokehTornado({'/bkapp': bkapp}, extra_websocket_origins=["localhost:8000","127.0.0.1:8000",])
    # Der Tornado Http-Server
    bokeh_http = HTTPServer(bokeh_tornado)
    # und sein Websocket
    bokeh_http.add_sockets(sockets)

    # Hier wird von Bokeh der Eventloop mit der Bokeh-Instanz un ddem Tornato-Webserver verheiratet
    server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()

# Ein Thread pro Gunicorn worker
from threading import Thread
Thread(target=bk_worker).start()

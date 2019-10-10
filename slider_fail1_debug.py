# Numercal Python importieren
import numpy as np

# Bokeh Abhängigkeiten
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.widgets import Slider

# importiere Zeitbibliothek
from time import sleep, time

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

# wir holen uns eine Datei für das logging
log = open('/tmp/bokeh.log', 'a')

# Diese Funktion soll gerufen werden, wenn der Schieberegler sich ändert ..
def update_data(attrname, old, new):
    k = freq.value
    x = np.linspace(0, X_MAX, N)
    y = np.sin(k*x)
    source.data =dict(x=x, y=y)
    # füge eine fiktive Berechnugns-Zeit von einer Sekunde ein
    sleep(1)
    # Wir schreiben den log
    log_line_template = "%s: attribute: %s, old: %s, new: %s\n"
    log_line = log_line_template % (time.time(), attrname, old, new)
    log.write(log_line)

# .. was hier verdrahtet wird
freq.on_change('value', update_data)

# Hier wird eine Box im Browser erzeut, welche den Schieberegler enthält
inputs = widgetbox(freq)

# Diese Box wir im HTML-Document mit dem Plot in einer Zeile ausgerichtet
curdoc().add_root(row(inputs, plot, width=800))

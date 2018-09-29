from bokeh.embed import components
from bokeh.resources import CDN

from flask import Flask
from flask import render_template

from static import root

app = Flask(__name__)
    
    
@app.route('/')
def index():
    # Hier wird bokeh aufgerufen um das Script und das div tag zu erzeugen
    bokeh_script, bokeh_div = components( root() )
    # Diese werden dem Flask Template zum einbetten übergeben     
    return render_template('bokeh.jinja', bokeh_script=bokeh_script, bokeh_div=bokeh_div, CDN=CDN.render())
    
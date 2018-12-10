"""

TODO: make a SQL database:
http://flask.pocoo.org/docs/1.0/tutorial/database/

"""

# Standard library imports
import datetime

# Third party imports
import pandas as pd

# Local application imports
from scripts import settings

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
# @app.route('/<var>')
def home():
    load_time = datetime.datetime.now()

    return render_template('home.html', load_time=load_time)

@app.route('/attack')
@app.route('/attack/<gen>')
def attack(gen=None, result_table=None):
    if gen is not None:
        settings.init(GEN=gen, METHOD='harmonic_mean')

        N = 10

        with pd.HDFStore(settings.result_filepath, mode='r') as store:
            results = store['result']
            vectors = store['vectors']

        # results = results.head()
        result_table = results.to_html()

    return render_template('attack.html', gen=gen, result_table=result_table)

@app.route('/defense')
@app.route('/defense/<gen>')
def defense(gen=None):
    return render_template('defense.html', gen=gen)

@app.route('/combined')
@app.route('/combined/<gen>')
def combined(gen=None):
    return render_template('combined.html', gen=gen)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)

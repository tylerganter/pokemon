"""

TODO: make a SQL database:
http://flask.pocoo.org/docs/1.0/tutorial/database/

"""

# TODO CONTINUE HERE - test the VM and deploy

# Standard library imports
import os
import sys
import datetime

# Third party imports
# import pandas as pd

# Local application imports
sys.path.append(os.path.abspath("./scripts"))
import settings, analysis

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    load_time = datetime.datetime.now()

    return render_template('home.html', load_time=load_time)

@app.route('/attack')
@app.route('/attack/<gen>')
def attack(gen=None, result_table=None):
    if gen is not None:
        settings.init(GEN=gen, METHOD='harmonic_mean')

        moves_and_scores, damage_matrix = analysis.load_results()

        moves_and_scores = moves_and_scores.sort_values(by=['a_score'], ascending=False)
        moves_and_scores = moves_and_scores.reset_index(drop=True)

        result_table = moves_and_scores.to_html()

    return render_template('attack.html', gen=gen, result_table=result_table)

@app.route('/defense')
@app.route('/defense/<gen>')
def defense(gen=None, result_table=None):
    if gen is not None:
        settings.init(GEN=gen, METHOD='harmonic_mean')

        moves_and_scores, damage_matrix = analysis.load_results()

        moves_and_scores = moves_and_scores.sort_values(by=['d_score'])
        moves_and_scores = moves_and_scores.reset_index(drop=True)

        result_table = moves_and_scores.to_html()

    return render_template('defense.html', gen=gen, result_table=result_table)

@app.route('/combined')
@app.route('/combined/<gen>')
def combined(gen=None, result_table=None):
    if gen is not None:
        settings.init(GEN=gen, METHOD='harmonic_mean')

        moves_and_scores, damage_matrix = analysis.load_results()

        moves_and_scores = moves_and_scores.sort_values(by=['ad_score'], ascending=False)
        moves_and_scores = moves_and_scores.reset_index(drop=True)

        result_table = moves_and_scores.to_html()

    return render_template('combined.html', gen=gen, result_table=result_table)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)

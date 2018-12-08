"""
To activate virtual environment

    . venv/bin/activate


To install requirements (make sure venv is activated!)

-t lib: This flag copies the libraries into a lib folder, which uploads to App Engine during deployment.

-r requirements.txt: Tells pip to install everything from requirements.txt.

    pip install -t lib -r requirements.txt

"""

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    # return render_template('home.html')
    return 'Hello Brock and Misty!'

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

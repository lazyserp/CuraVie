# main file to run the server
from flask import Flask,render_template,request,jsonify
from flask_bcrypt import Bcrypt

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html.j2")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1> Hello, Saimon! You have Successfully executed the Flask Program. </h1>"

if __name__ == '__main__':
    app.run (debug=True)
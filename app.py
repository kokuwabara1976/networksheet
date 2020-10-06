from flask import Flask, request, redirect, render_template, url_for, jsonify

app = Flask(__name__)
app.secret_key = "aVerySecretKey"
PORT = 8081

@app.route("/")
def landing():
    return render_template('landing.html')


@app.route("/network")
def network():
    return render_template('network.html')


@app.route("/getnodes")
def getnodes():

	nodes = [
      {
        "id": 'MM',
        "x": 469,
        "y": 410,
        "type": 'X'
      },
      {
        "id": 'RS',
        "x": 480,
        "y": 450,
        "type": 'X'
      },
      {
        "id": 'TM',
        "x": 400,
        "y": 400,
        "type": 'X'
      }
    ]

	return jsonify(nodes)


if __name__ == "__main__":
    app.run(debug=False, port=PORT)




from flask import Flask, request, redirect, render_template, url_for, jsonify, session
import io
import matplotlib.pyplot as plt
import pandas as pd

# https://bl.ocks.org/nitaku/7512487

app = Flask(__name__)
app.secret_key = "aVerySecretKey"
PORT = 8081

@app.route("/")
def landing():
    return render_template('landing.html')

@app.route("/who", methods=['GET', 'POST'])
def who():

	if request.method == 'POST':

		nodes = []

		who = request.form

		df = pd.DataFrame({})

		for headline in ['technical', 'insider', 'political', 'guidance', 'inspiration', 'friendship']:
		    _df = pd.DataFrame({'names': who.getlist(headline), 'category': headline})
		    df = pd.concat([df, _df])

		df = df[df['names'] != '']
		df = df.reset_index(drop=True).groupby('names')['category'].agg(lambda x: str(list(x)))

		for name,categories in df.items():

			nodes.append(
			    	{
			    	 "id": name,
			    	 "name": name,
			    	 "x": 469,
			    	 "y": 410,
			    	 "type": categories,
			    	 "img": "/static/img/favicon.ico",
			    	 }
		    	 )

		session['nodes'] = nodes

		return render_template('how.html', nodes=session['nodes'])


	return render_template('who.html')


@app.route("/how", methods=['GET', 'POST'])
def how():

	if request.method == 'POST':

		session['how'] = request.form

		return render_template('network.html')

	return render_template('how.html')


@app.route("/network", methods=['GET', 'POST'])
def network():

    return render_template('network.html')


#### Internal Endpoints

@app.route("/getnodes")
def getnodes():

	nodes = session['nodes']

	return jsonify(nodes)

@app.route("/postnodes", methods=['GET','POST'])
def postnodes():

	print(request.data)

	return redirect(url_for("postnodes"))


if __name__ == "__main__":
    app.run(debug=False, port=PORT)




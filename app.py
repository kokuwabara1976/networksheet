from flask import Flask, request, redirect, render_template, url_for, jsonify, session
import io
import pandas as pd
import json

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

			print(categories)
			print(type(categories))

			nodes.append(
			    	{
			    	 "id": name,
			    	 "name": name,
			    	 "x": 469,
			    	 "y": 410,
			    	 "type": ', '.join(eval(categories)),
			    	 # "img": "/static/img/favicon.ico",
			    	 }
		    	 )

		session['nodes'] = nodes

		return render_template('how.html', nodes=session['nodes'])


	return render_template('who.html')


@app.route("/how", methods=['GET', 'POST'])
def how():

	d = {"close": "You are",
	     "work": "You talk to them at work",
	     "outside": "You talk to them outside of work",
	     "help": "They come to you for help, feedback, or a chat",
	     "know": "You know about their",
	     "similar": "You are similar in"
	}

	if request.method == 'POST':

		answers = {}

		for ques_name, ans in request.form.lists():

			name = ques_name.split("_")[1]
			ques = ques_name.split("_")[0]

			answers[name] = {}

		for ques_name, ans in request.form.lists():

			name = ques_name.split("_")[1]
			ques = ques_name.split("_")[0]
			answers[name].update({d[ques]: ans})

		session['how'] = answers

		return render_template('network.html', nodes=json.dumps(session['nodes']))

	return render_template('how.html')


@app.route("/network", methods=['GET', 'POST'])
def network():

    return render_template('network.html', nodes=json.dumps(session['nodes']), summary=session['how'])


@app.route("/pie", methods=['GET', 'POST'])
def pie():

    return render_template('pie.html')

@app.route("/summary", methods=['GET', 'POST'])
def summary():

	return render_template('summary.html', img=session['graph'], summary=session['how'])


#### Internal Endpoints

@app.route("/getnodes")
def getnodes():

	nodes = session['nodes']

	return jsonify(nodes), 200, {'Content-Type': 'application/json'}

# @app.route("/postnodes", methods=['GET','POST'])
# def postnodes():

# 	print(request)

# 	return redirect(url_for("postnodes"))


@app.route("/postgraph", methods=['GET','POST'])
def postgraph():

    session['graph'] = request.data.decode('utf-8')

    return jsonify(dict(redirect='summary'))



if __name__ == "__main__":
    app.run(debug=False, port=PORT)




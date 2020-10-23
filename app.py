from flask import Flask, request, redirect, render_template, url_for, jsonify, session
import io
import pandas as pd
import json
import numpy as np

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

		for headline in ['T', 'N', 'political', 'G', 'I', 'F']:
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
			    	 }
		    	 )

		session['nodes'] = nodes

		return redirect(url_for('how'))

	return render_template('who.html')


@app.route("/how", methods=['GET', 'POST'])
def how():

	if request.method == 'POST':

        # x,y for x,y in request.form.lists()
		# similar_MM ['Gender']
		# similar_EE ['Gender', 'Age', 'Country or culture', 'Professional Interests']
		# help_CC ['Never']

		names = np.unique([ques_name.split("_")[1] for ques_name, ans in request.form.lists()]).tolist()

		score_to_pie = {"1-2 times a year": "/static/img/1_4.png", 
		                "Rather distant": "/static/img/1_4.png",
                        "Every few months":"/static/img/2_4.png",
                        "Somewhat close":"/static/img/2_4.png",
                        "Every month":"/static/img/3_4.png",
                        "Rather close":"/static/img/3_4.png",
                        "Every week":"/static/img/4_4.png",
                        "Very close":"/static/img/4_4.png"}

		score_to_pie_6 = {0: "/static/img/0_4.png",
		                  1: "/static/img/1_6.png", 
		                  2: "/static/img/2_6.png",
		                  3: "/static/img/2_4.png",
		                  4: "/static/img/4_6.png",
		                  5: "/static/img/5_6.png",
		                  6: "/static/img/4_4.png"}

		score = {}

		for name in names:
			score[name] = {}

		for quest in ['close', 'work', 'outside', 'help', 'know', 'similar'] :

			for name in names:
				key = quest + "_" + name

				ans = [y for x,y in request.form.lists() if x == key]

				if quest in ['close', 'help', 'outside', 'work']:
					score[name][quest] = score_to_pie[ans[0][0]]
				else:
					if len(ans) == 0:
						score[name][quest] = score_to_pie_6[0]
					else:
					    score[name][quest] = score_to_pie_6[len(ans[0])]

		session['how'] = score

		return redirect(url_for('network'))


	return render_template('how.html', nodes=session['nodes'])


@app.route("/network", methods=['GET', 'POST'])
def network():

	return render_template('network.html', nodes=json.dumps(session['nodes']), summary=session['how'])


@app.route("/pie", methods=['GET', 'POST'])
def pie():

    return render_template('pie.html')

@app.route("/summary", methods=['GET', 'POST'])
def summary():

	print(session['how'])

	return render_template('summary.html', img=session['graph'], summary=session['how'])

@app.route("/summarypie", methods=['GET', 'POST'])
def summarypie():

	return render_template('summary_pie.html')


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




from flask import Flask, request, redirect, render_template, url_for, jsonify, session, Response
from collections import defaultdict #added 1/10/2025
import io
import csv
import pandas as pd
import json
import numpy as np

# https://bl.ocks.org/nitaku/7512487

app = Flask(__name__)
app.secret_key = "aVerySecretKey"
PORT = 8081

SCORE_TO_PIE = {"1-2 times a year": "/static/img/1_4.png",
                "Rather distant": "/static/img/1_4.png",
                "Every few months": "/static/img/2_4.png",
                "Somewhat close": "/static/img/2_4.png",
                "Every month": "/static/img/3_4.png",
                "Rather close": "/static/img/3_4.png",
                "Every week": "/static/img/4_4.png",
                "Very close": "/static/img/4_4.png"}

SCORE_TO_PIE_6 = {0: "/static/img/0_4.png",
                  1: "/static/img/1_6.png",
                  2: "/static/img/2_6.png",
                  3: "/static/img/2_4.png",
                  4: "/static/img/4_6.png",
                  5: "/static/img/5_6.png",
                  6: "/static/img/4_4.png"}


def compute_how(raw):
    score = {}
    for name, answers in raw.items():
        score[name] = {}
        for quest, value in answers.items():
            if quest in ['close', 'help', 'outside', 'work']:
                score[name][quest] = SCORE_TO_PIE[value]
            else:
                score[name][quest] = SCORE_TO_PIE_6[len(value)]
    return score

@app.route("/")
def landing():
    return render_template('landing.html')

@app.route("/who", methods=['GET', 'POST'])  
def who():  
    if request.method == 'POST':  
        nodes = []  
        who = request.form  

        # Use a defaultdict to efficiently group names and categories  
        name_categories = defaultdict(list)  
        for headline in ['T', 'N', 'P', 'G', 'I', 'F']:  
            for name in who.getlist(headline):  
                if name:  # More efficient than df[df['names'] != '']  
                    name_categories[name].append(headline)  

        # Create nodes directly from the defaultdict  
        for name, categories in name_categories.items():  
            nodes.append({  
                "id": name,  
                "name": name,  
                "x": 469,  
                "y": 410,  
                "type": ', '.join(categories),  # No need for string conversion and eval  
                "cats": categories  
            })  

        nodes.sort(key=lambda n: n["id"].lower())
        session['nodes'] = nodes

        # Drop stale how-answers for contacts that no longer exist (removed or renamed)
        current_names = {n["id"] for n in nodes}
        session['how_raw'] = {name: answers for name, answers in session.get('how_raw', {}).items() if name in current_names}
        session['how'] = {name: answers for name, answers in session.get('how', {}).items() if name in current_names}

        return redirect(url_for('how'))

    return render_template('who.html', nodes=session.get('nodes', []))


@app.route("/how", methods=['GET', 'POST'])
def how():

	if request.method == 'POST':

        # x,y for x,y in request.form.lists()
		# similar_MM ['Gender']
		# similar_EE ['Gender', 'Age', 'Country or culture', 'Professional Interests']
		# help_CC ['Never']

		names = set()  # Use a set for efficient unique name collection  
		for ques_name, _ in request.form.items(): # Iterate through items view, not lists
			name = ques_name.split("_")[1]
			names.add(name)
		names = list(names)  # Convert to list if needed later

		raw = {}

		for name in names:
			raw[name] = {}

		for quest in ['close', 'work', 'outside', 'help', 'know', 'similar'] :

			for name in names:
				key = quest + "_" + name

				ans = [y for x,y in request.form.lists() if x == key]

				if quest in ['close', 'help', 'outside', 'work']:
					raw[name][quest] = ans[0][0]
				else:
					raw[name][quest] = ans[0] if ans else []

		session['how_raw'] = raw
		session['how'] = compute_how(raw)

		return redirect(url_for('network'))


	return render_template('how.html', nodes=session['nodes'], answers=session.get('how_raw', {}))


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


@app.route("/export_csv")
def export_csv():

    nodes = session.get('nodes', [])
    how_raw = session.get('how_raw', {})

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['id', 'cats', 'close', 'work', 'outside', 'help', 'know', 'similar'])

    for node in nodes:
        answers = how_raw.get(node['id'], {})
        writer.writerow([
            node['id'],
            ';'.join(node['cats']),
            answers.get('close', ''),
            answers.get('work', ''),
            answers.get('outside', ''),
            answers.get('help', ''),
            ';'.join(answers.get('know', [])),
            ';'.join(answers.get('similar', [])),
        ])

    return Response(buf.getvalue(), mimetype='text/csv',
                     headers={'Content-Disposition': 'attachment; filename=networksheet_data.csv'})


@app.route("/import_csv", methods=['POST'])
def import_csv():

    file = request.files['file']
    reader = csv.DictReader(io.StringIO(file.read().decode('utf-8-sig')))

    nodes = []
    raw = {}

    for row in reader:
        name = row['id']
        cats = [c for c in row['cats'].split(';') if c]
        nodes.append({
            "id": name,
            "name": name,
            "x": 469,
            "y": 410,
            "type": ', '.join(cats),
            "cats": cats
        })

        answers = {}
        for quest in ['close', 'work', 'outside', 'help']:
            if row.get(quest):
                answers[quest] = row[quest]
        for quest in ['know', 'similar']:
            if row.get(quest):
                answers[quest] = [v for v in row[quest].split(';') if v]
        if answers:
            raw[name] = answers

    nodes.sort(key=lambda n: n["id"].lower())
    session['nodes'] = nodes
    session['how_raw'] = raw
    session['how'] = compute_how(raw)

    return redirect(url_for('who'))


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




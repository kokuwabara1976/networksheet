from flask import Flask, request, redirect, render_template, url_for, jsonify, session, Response
from collections import defaultdict #added 1/10/2025
import io
import csv
import math
import pandas as pd
import json
import numpy as np

# https://bl.ocks.org/nitaku/7512487

app = Flask(__name__)
app.secret_key = "aVerySecretKey"
PORT = 8081

CLOSE_LEVELS = ["Rather distant", "Somewhat close", "Rather close", "Very close"]
FREQ_LEVELS = ["1-2 times a year", "Every few months", "Every month", "Every week"]

QUEST_LEVELS = {"close": CLOSE_LEVELS, "work": FREQ_LEVELS, "outside": FREQ_LEVELS, "help": FREQ_LEVELS}

KNOW_LABELS = ["Friends", "Family", "Education", "Culture", "Interests or hobbies", "Favorite Food"]
SIMILAR_LABELS = ["Gender", "Age", "Country or culture of origin", "Professional Interests", "Social or political attitudes", "Personality"]

QUEST_LABELS = {"know": KNOW_LABELS, "similar": SIMILAR_LABELS, **QUEST_LEVELS}


def compute_how(raw):
    score = {}
    for name, answers in raw.items():
        score[name] = {}
        for quest, value in answers.items():
            if quest in QUEST_LEVELS:
                score[name][quest] = QUEST_LEVELS[quest].index(value) + 1
            else:
                score[name][quest] = value
    return score


def wrap_label(label, max_chars=10):
    if len(label) <= max_chars:
        return [label]
    words = label.split(' ')
    if len(words) == 1:
        return [label]
    best_i, best_diff = 1, None
    for i in range(1, len(words)):
        diff = abs(len(' '.join(words[:i])) - len(' '.join(words[i:])))
        if best_diff is None or diff < best_diff:
            best_i, best_diff = i, diff
    return [' '.join(words[:best_i]), ' '.join(words[best_i:])]


def render_pie(labels, filled, size=100):
    n = len(labels)
    wedge_angle = 360 / n
    cx = cy = size / 2
    r = size / 2 - 2
    font_size = 6 if n <= 4 else 5.2

    def point(angle_deg):
        angle_rad = math.radians(angle_deg)
        return cx + r * math.sin(angle_rad), cy - r * math.cos(angle_rad)

    parts = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">']

    for i, label in enumerate(labels):
        start_angle = i * wedge_angle
        end_angle = start_angle + wedge_angle
        x1, y1 = point(start_angle)
        x2, y2 = point(end_angle)
        fill = "#008000" if filled[i] else "#dbe9df"
        large_arc = 1 if wedge_angle > 180 else 0
        path = f'M {cx},{cy} L {x1:.2f},{y1:.2f} A {r},{r} 0 {large_arc},1 {x2:.2f},{y2:.2f} Z'
        parts.append(f'<path d="{path}" fill="{fill}" stroke="#ffffff" stroke-width="1.2"><title>{label}</title></path>')

        mid_angle = start_angle + wedge_angle / 2
        rotation = mid_angle - 90
        if 90 < rotation % 360 < 270:
            rotation += 180

        lines = wrap_label(label, max_chars=10 if n <= 4 else 9)
        label_r = r * 0.6
        lx = cx + label_r * math.sin(math.radians(mid_angle))
        ly = cy - label_r * math.cos(math.radians(mid_angle))
        line_height = font_size * 1.15

        if len(lines) == 1:
            content = lines[0]
        else:
            tspans = []
            for idx, line in enumerate(lines):
                dy = -line_height / 2 if idx == 0 else line_height
                tspans.append(f'<tspan x="{lx:.2f}" dy="{dy:.2f}">{line}</tspan>')
            content = ''.join(tspans)

        parts.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" font-size="{font_size}" fill="#04342C" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'transform="rotate({rotation:.2f} {lx:.2f} {ly:.2f})">{content}</text>'
        )

    parts.append('</svg>')
    return ''.join(parts)


app.jinja_env.globals['render_pie'] = render_pie

@app.route("/")
def landing():
    return render_template('landing.html')

@app.route("/new_session")
def new_session():

    session.clear()

    return redirect(url_for('who'))


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

	return render_template('network.html', nodes=json.dumps(session['nodes']), summary=session['how'], wedge_labels=QUEST_LABELS)


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




from flask import Flask, request, redirect, render_template, url_for, jsonify, session, Response
from collections import defaultdict #added 1/10/2025
import io
import csv
import math
import uuid
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

KNOW_VALUES = ["Friends", "Family", "Education", "Culture", "Interests or hobbies", "Favorite Food"]
SIMILAR_VALUES = ["Gender", "Age", "Country or culture of origin", "Professional Interests", "Social or political attitudes", "Personality"]

# Shortened text for the pie wedge itself; the full value is still what's matched against raw answers.
SIMILAR_DISPLAY = {
    "Country or culture of origin": "Culture",
    "Professional Interests": "Interests",
    "Social or political attitudes": "Soc/pol attitudes",
}

# "help" reuses the same 4 raw frequency values as work/outside, but displays balance wording.
HELP_DISPLAY = {
    "1-2 times a year": "Quite unbalanced",
    "Every few months": "Slightly unbalanced",
    "Every month": "Generally balanced",
    "Every week": "Very balanced",
}


def wedge_pairs(values, display_overrides=None):
    display_overrides = display_overrides or {}
    return [(v, display_overrides.get(v, v)) for v in values]


QUEST_LABELS = {
    "close": wedge_pairs(CLOSE_LEVELS),
    "work": wedge_pairs(FREQ_LEVELS),
    "outside": wedge_pairs(FREQ_LEVELS),
    "help": wedge_pairs(FREQ_LEVELS, HELP_DISPLAY),
    "know": wedge_pairs(KNOW_VALUES),
    "similar": wedge_pairs(SIMILAR_VALUES, SIMILAR_DISPLAY),
}


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


def wrap_label(label):
    words = label.split(' ')
    if len(words) == 1:
        return [label]
    best_i, best_diff = 1, None
    for i in range(1, len(words)):
        diff = abs(len(' '.join(words[:i])) - len(' '.join(words[i:])))
        if best_diff is None or diff < best_diff:
            best_i, best_diff = i, diff
    return [' '.join(words[:best_i]), ' '.join(words[best_i:])]


def render_pie(labels, filled, size=170, top_label=None):
    n = len(filled)
    wedge_angle = 360 / n
    cx = cy = size / 2
    r = size / 2 - 35
    label_r = r + 14
    font_size = 12 if n <= 4 else 10.4
    uid = uuid.uuid4().hex[:8]
    counter = [0]

    def point(angle_deg, radius):
        angle_rad = math.radians(angle_deg)
        return cx + radius * math.sin(angle_rad), cy - radius * math.cos(angle_rad)

    svg_open = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
    )
    defs = ['<defs>']
    body = []

    def add_curved_label(text, mid_angle, radius):
        # canvg's textPath support truncates whenever startOffset is non-zero, regardless
        # of text-anchor (verified empirically) - so instead of centering via startOffset,
        # shift the underlying path's own start angle back by half the estimated text
        # width and always render at startOffset=0, which is the one combination canvg
        # renders in full rather than clipping.
        flip = 90 < mid_angle % 360 < 270
        text_width = len(text) * font_size * 0.62 + 4
        half_width_deg = math.degrees((text_width / 2) / radius)
        label_start_angle = mid_angle - half_width_deg
        label_end_angle = mid_angle + half_width_deg
        label_large_arc = 1 if abs(label_end_angle - label_start_angle) > 180 else 0

        a1, a2 = (label_end_angle, label_start_angle) if flip else (label_start_angle, label_end_angle)
        sweep = 0 if flip else 1
        lx1, ly1 = point(a1, radius)
        lx2, ly2 = point(a2, radius)
        counter[0] += 1
        path_id = f'wedge-label-{uid}-{counter[0]}'
        defs.append(
            f'<path id="{path_id}" d="M {lx1:.2f},{ly1:.2f} A {radius:.2f},{radius:.2f} 0 {label_large_arc},{sweep} '
            f'{lx2:.2f},{ly2:.2f}" fill="none"/>'
        )
        body.append(
            f'<text font-size="{font_size}" fill="#04342C">'
            f'<textPath href="#{path_id}" xlink:href="#{path_id}" startOffset="0">{text}</textPath>'
            f'</text>'
        )

    for i in range(n):
        start_angle = i * wedge_angle
        end_angle = start_angle + wedge_angle
        x1, y1 = point(start_angle, r)
        x2, y2 = point(end_angle, r)
        fill = "#008000" if filled[i] else "#dbe9df"
        large_arc = 1 if wedge_angle > 180 else 0
        path = f'M {cx},{cy} L {x1:.2f},{y1:.2f} A {r},{r} 0 {large_arc},1 {x2:.2f},{y2:.2f} Z'
        title = labels[i] if i < len(labels) else ''
        body.append(f'<path d="{path}" fill="{fill}" stroke="#ffffff" stroke-width="1.2"><title>{title}</title></path>')

    if top_label is not None:
        # A single answer, no longer competing with other wedge labels - render it
        # as plain (non-curved) text centered on the pie itself, like a donut-chart
        # center label, rather than perimeter text (which was hard to keep centered).
        inner_r = r * 0.55
        text_width = len(top_label) * font_size * 0.62 + 4
        lines = wrap_label(top_label) if text_width > inner_r * 1.8 else [top_label]
        line_height = font_size * 1.15
        n_lines = len(lines)
        tspans = []
        for li, line in enumerate(lines):
            dy = -line_height * (n_lines - 1) / 2 if li == 0 else line_height
            tspans.append(f'<tspan x="{cx}" dy="{dy:.2f}">{line}</tspan>')
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{inner_r:.2f}" fill="#ffffff"/>')
        body.append(
            f'<text x="{cx}" y="{cy}" font-size="{font_size}" fill="#04342C" '
            f'text-anchor="middle" dominant-baseline="middle">{"".join(tspans)}</text>'
        )
    else:
        for i, label in enumerate(labels):
            mid_angle = i * wedge_angle + wedge_angle / 2
            flip = 90 < mid_angle % 360 < 270
            own_arc_length = label_r * math.radians(wedge_angle)
            text_width = len(label) * font_size * 0.62 + 4
            lines = wrap_label(label) if text_width > own_arc_length else [label]
            line_gap = font_size * 1.15
            n_lines = len(lines)
            for li, line in enumerate(lines):
                # Larger radius sits higher on screen for top-half wedges and lower for
                # bottom-half ones (flipped) - order lines so reading top-to-bottom on
                # screen matches the label's natural left-to-right word order.
                idx = li if flip else (n_lines - 1 - li)
                radius = label_r + (idx - (n_lines - 1) / 2) * line_gap
                add_curved_label(line, mid_angle, radius)

    defs.append('</defs>')
    return svg_open + ''.join(defs) + ''.join(body) + '</svg>'


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




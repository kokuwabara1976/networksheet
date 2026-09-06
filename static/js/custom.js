
var img_result = document.getElementById('img_result');
var img_back = document.getElementById('background');
var img_header = document.getElementById('background_header');
var img_footer = document.getElementById('background_footer');
var img_arrow = document.getElementById('arrow');

function svgCellToDataURL(td) {
	var svgEl = td.querySelector('svg');
	var xml = new XMLSerializer().serializeToString(svgEl);
	var canvas = document.createElement('canvas');
	canvas.width = parseInt(svgEl.getAttribute('width'), 10);
	canvas.height = parseInt(svgEl.getAttribute('height'), 10);
	var ctx = canvas.getContext('2d');
	var v = canvg.Canvg.fromString(ctx, xml);
	v.start();
	return canvas.toDataURL('image/png');
}

function generatePDF() {
	
	doc = new jsPDF('p', 'in', 'letter');
	doc.addFont('Roboto-Light.ttf', 'roboto_light', 'normal');
	doc.addFont('Roboto-Bold.ttf', 'roboto_bold', 'normal');
	doc.addFont('Roboto-Regular.ttf', 'roboto_regular', 'normal');
	doc.addFont('Marmelad-Regular.ttf', 'marmelad', 'bold');
	doc.addFont('Marmelad-Regular.ttf', 'marmelad', 'normal');

	// first page
    doc.addImage(img_back, 'JPEG', 0, 0, 10, 11);
    doc.addImage(img_arrow, 'PNG', 6.8, 4.55, 0.3, 0.15);

	doc.setFontSize(40);
	doc.setTextColor(255, 255, 255);
	doc.setFont("marmelad");
	doc.text(3, 4, "NETWORKsheet");
	doc.setFontSize(20);
	doc.text(3, 4.7, "Your NETWORKsheet Report");

	doc.setLineWidth(0.05);
	doc.setDrawColor(255, 255, 255);
	doc.line(3, 4.2, 7.25, 4.2);

	// second page
	doc.addPage("", "");
    doc.addImage(img_header, 'JPEG', 0, 0, 8.5, 1.4);
    doc.addImage(img_footer, 'JPEG', 0, 10, 8.5, 1.3);

	doc.text(0.4, 0.75, "NETWORKsheet");
	doc.setLineWidth(0.02);
	doc.setDrawColor(255, 255, 255);
	doc.line(0.4, 0.82, 2.5, 0.82);
	doc.setDrawColor(0);
	doc.setFillColor(240, 240, 240);
	doc.rect(0, 1.4, 10, 1.2, "F");

	var str = "Your network report is below.Keep in mind that this report is not meant to be comprehensive \nanalysis of your entire network.Rather, it is designed to help you reflect on your general networking \npatterns by thinking about the people who comprise your core professional network.";
	doc.setFontSize(13);
	doc.setFont("roboto_light");
	doc.setTextColor(32, 33, 36);
	doc.text(0.45, 1.8, str);

	doc.setFontSize(13);
	doc.setFont("roboto_bold");
	doc.setTextColor(46, 108, 83);
	doc.text(0.4, 3.1, "1 / 2");

	doc.setFontSize(15);
	doc.setFont("roboto_bold");
	doc.setTextColor(32, 33, 36);
	doc.text(0.4, 3.5, "HOW STRONG ARE YOUR RELATIONSHIPS?");

	str = "The pie charts below indicate how strong your relationships are across different dimensions. The \nmore green the pie chart is, the stronger the relationship on a given dimension.";
	doc.setFontSize(13);
	doc.setFont("roboto_light");
	doc.setTextColor(32, 33, 36);
	doc.text(0.4, 3.9, str);
	doc.text(0.4, 4.5, "Do you see any weak relationships? In what ways are they weak?");

	doc.setFontSize(11);
    doc.setFont("roboto_bold");
    doc.setTextColor(46, 108, 83);
    doc.text(0.4, 5.2, "Response keys");

    doc.setFontSize(9);
    doc.setFont("roboto_light");
    doc.setTextColor(32, 33, 36);
    doc.text(0.4, 5.4, "How close are you? [1/4=rather distant, 2/4=somewhat close, 3/4=rather close, 4/4=very close]");

    doc.setFontSize(9);
    doc.setFont("roboto_light");
    doc.setTextColor(32, 33, 36);
    doc.text(0.4, 5.6, "How often do you talk during work? [1/4=0-2 times a year, 2/4=every few months, 3/4=every month, 4/4=every week]");

	doc.setFontSize(9);
    doc.setFont("roboto_light");
    doc.setTextColor(32, 33, 36);
    doc.text(0.4, 5.8, "How often do you talk outside of work? [1/4=0-2 times a year, 2/4=every few months, 3/4=every month, 4/4=every week]");

    doc.setFontSize(9);
    doc.setFont("roboto_light");
    doc.setTextColor(32, 33, 36);
    doc.text(0.4, 6., "How balanced are your relationships? [1/4=quite unbalanced, 2/4=slightly unbalanced, 3/4=generally balanced, 4/4=very balanced]");

	doc.setFontSize(9);
    doc.setFont("roboto_light");
    doc.setTextColor(32, 33, 36);
    doc.text(0.4, 6.2, "What do you know about them? [0/6=nothing, 6/6=a lot: friends, family, education, cultural background, interests, food]");

	doc.setFontSize(9);
    doc.setFont("roboto_light");
    doc.setTextColor(32, 33, 36);
    doc.text(0.4, 6.4, "How similar are you? [0/6=not at all, 6/6=very much: gender, age, cultural background, interests, social or political attitudes, personality]");

	//doc.addPage("", "");

	str = [
		"Contacts",
		"How close \nare you?",
		"How often do \nyou talk at \nwork?",
		"How often \ndo you talk \noutside of \nwork?",
		"How balanced \nare your \nrelationships?",
		"What do you \nknow about \n them?",
		"How similar \nare you?"
	];
	doc.setFont("roboto_regular");
	doc.setFontSize(11);
	for (var i = 0; i < 7; i++) {
		doc.setDrawColor(0);
		doc.setFillColor(240, 240, 240);
		var x = 0.4 + 1.09 * i;
		doc.rect(x, 6.8, 1.06, 0.85, "F"); //doc.rect(x, 4.8, 1.06, 0.85, "F");
		doc.text(x+0.05, 7, str[i]);
	}

	var tr = document.getElementsByClassName('tr_result');
	for (var i = 0; i < tr.length; i++) {
		if (i > 1) break;
		var td = tr[i].children;
		for (var j = 0; j < 7; j++) {
			if (j == 0) {
				doc.setFont("roboto_regular");
				doc.setFontSize(13);
				doc.setTextColor(46, 108, 83);
				doc.text(0.5, 8.25+i*1, td[j].innerHTML);
			} else {
				doc.addImage(svgCellToDataURL(td[j]), 'PNG', 0.45+j*1.09, 7.66+i*1, 1, 1);
			}
		}
	}

    var offset = 0;
    if (tr.length > 1) { //if (tr.length > 3) {
    	for (var i = 2; i < tr.length; i++) {
    		if ((i - 2) % 7 == 0) {
				doc.addPage("", "");
				str = [
					"Contact",
					"How close \nare you?",
					"How often do \nyou talk at \nwork?",
					"How often \ndo you talk \noutside of \nwork?",
					"How balanced \nare your \nrelationships?",
					"What do you \nknow about \n them?",
					"How similar \nare you?"
				];
				doc.setFont("roboto_regular");
				doc.setFontSize(11);
				doc.setTextColor(32, 33, 36);
				for (var j = 0; j < 7; j++) {
					doc.setDrawColor(0);
					doc.setFillColor(240, 240, 240);
					var x = 0.4 + 1.09 * j;
					doc.rect(x, 1.8, 1.06, 0.85, "F");
					doc.text(x+0.05, 2, str[j]);
				}
				doc.addImage(img_header, 'JPEG', 0, 0, 8.5, 1.4);
				doc.addImage(img_footer, 'JPEG', 0, 10, 8.5, 1.3);

				doc.setTextColor(255, 255, 255);
				doc.setFontSize(20);
				doc.setFont("marmelad");
				doc.text(0.4, 0.75, "NETWORKsheet");
				doc.setLineWidth(0.02);
				doc.setDrawColor(255, 255, 255);
				doc.line(0.4, 0.82, 2.5, 0.82);
				offset = i;
			}
			


			var td = tr[i].children;
			for (var j = 0; j < 7; j++) {
				if (j == 0) {
					doc.setFont("roboto_regular");
					doc.setFontSize(13);
					doc.setTextColor(46, 108, 83);
					doc.text(0.5, 3.4+(i-offset)*1, td[j].innerHTML);
				} else {
					doc.addImage(svgCellToDataURL(td[j]), 'PNG', 0.45+j*1.09, 2.8+(i-offset)*1, 1, 1);
				}
			}
    	}
    }

	// last page
	doc.addPage("", "");
    doc.addImage(img_header, 'JPEG', 0, 0, 8.5, 1.4);
    doc.addImage(img_footer, 'JPEG', 0, 10, 8.5, 1.3);

	doc.setTextColor(255, 255, 255);
	doc.setFontSize(20);
	doc.setFont("marmelad");
	doc.text(0.4, 0.75, "NETWORKsheet");
	doc.setLineWidth(0.02);
	doc.setDrawColor(255, 255, 255);
	doc.line(0.4, 0.82, 2.5, 0.82);

	doc.setFontSize(13);
	doc.setFont("roboto_bold");
	doc.setTextColor(46, 108, 83);
	doc.text(0.4, 1.8, "2 / 2");

	doc.setFontSize(15);
	doc.setFont("roboto_bold");
	doc.setTextColor(32, 33, 36);
	doc.text(0.4, 2.1, "WHAT DOES YOUR NETWORK LOOK LIKE?");

	str = "Think about what it looks like. Do you see any empty cells? Crowded cells? Next to each \nperson's initials are letters indicating which types of support or benefits the person provides: \nT=technical support (problem-solving, expertise), N=news and information (opportunities, \nevents, or happenings at work), P=political support (securing resources, positions, opportunities), \nG=guidance (wisdom, feedback, mentoring), I=inspiration (energy, courage, creativity), F=friendship \n(social support, companionship). Do you see any missing benefits?";
	doc.setFontSize(13);
	doc.setFont("roboto_light");
	doc.setTextColor(32, 33, 36);
	doc.text(0.4, 2.6, str);

    doc.addImage(img_result.src, 'PNG', 0, 4, 9, 6);

	// string = doc.output('datauristring');
	// $('iframe').attr('src', string);

	doc.save('document.pdf');
}

$(document).ready(function () {

	$('#save_pdf').click(function() {
		if (document.querySelectorAll('.link').length === 0) {
			alert("Please draw your network first.");
			return;
		}
		var str_svg = $($('network svg')[0]).html();
		str_svg = str_svg.replace(/"/g, "'").replace("class='overlay'", "style='fill:transparent'");
		str_svg = "<svg>" + str_svg + "</svg>";
		var canvas = document.getElementById('svg_canvas');
		var ctx = canvas.getContext('2d');
		v = canvg.Canvg.fromString(ctx, str_svg);
		v.start();
		var data = canvas.toDataURL('image/jpeg');
		img_result.src = data;

		generatePDF();

	})

});
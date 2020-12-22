
var img_result = document.getElementById('img_result');
var img_back = document.getElementById('background');
var img_header = document.getElementById('background_header');
var img_footer = document.getElementById('background_footer');
var img_arrow = document.getElementById('arrow');

function generatePDF() {
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
	for (var i = 0; i < 7; i++) {
		doc.setDrawColor(0);
		doc.setFillColor(240, 240, 240);
		var x = 0.4 + 1.09 * i;
		doc.rect(x, 4.8, 1.06, 0.85, "F");
		doc.text(x+0.05, 5, str[i]);
	}

	var tr = document.getElementsByClassName('tr_result');
	for (var i = 0; i < tr.length; i++) {
		var td = tr[i].children;
		console.log(td[0].innerHTML);
		for (var j = 0; j < 7; j++) {
			if (j == 0) {
				doc.setFont("roboto_regular");
				doc.setFontSize(13);
				doc.setTextColor(46, 108, 83);
				doc.text(0.5, 6.25+i*1, td[j].innerHTML);
			} else {
				var img = td[j].children;
				doc.addImage(img[0], 'PNG', 0.45+j*1.09, 5.66+i*1, 1, 1);
			}
		}
	}

	// third page
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

	string = doc.output('datauristring');
	$('iframe').attr('src', string);

	// doc.save('document.pdf');
}

$(document).ready(function () {

	$('#save_pdf').click(function() {
		var str_svg = $($('svg')[0]).html();
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
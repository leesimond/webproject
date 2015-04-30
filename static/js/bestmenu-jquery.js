$(document).ready(function() {

	$("#about-btn").addClass('btn btn-primary').click( function(event) {
		msgstr = $("#msg").html()
			msgstr = msgstr + "o"
			$("#msg").html(msgstr)
	});

	$(".page-head").click( function(event) {
		alert("You clicked me! ouch!");
	});


});

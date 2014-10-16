
// Slide alert box down when clicking "successAlert" button
$(function () {
	$("#alertButton").on("click", function(e) {
		e.preventDefault();
		$("#successAlert").slideDown();
	});

	$("a.pop").on('click', function(e) {
		e.preventDefault();
	});

	$("a.pop").popover();
	$("[rel='tooltip']").tooltip();
})
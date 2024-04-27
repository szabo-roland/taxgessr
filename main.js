var puzzle;

function shuffle(array) {
  let currentIndex = array.length;

  // While there remain elements to shuffle...
  while (currentIndex != 0) {

    // Pick a remaining element...
    let randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    // And swap it with the current element.
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex], array[currentIndex]];
  }
}

function draw_buttons(index){
    if(puzzle["ancestors"].length <= index)
    {
	var box = $("#possibles");
	box.empty();
	box.text("WIN");
	return;
    }

    var ancestor = puzzle["ancestors"][index];
    var others = puzzle["other_choices"][ancestor["tax_id"]];
    var win_button = $('<button/>');
    win_button.text(ancestor["name"]);
    win_button.click(function () { draw_buttons(index + 1); });
    lose_buttons = [];
    if(others.length > 5)
    {
	others = others.slice(0, 5);
    }

    for(var i = 0; i < others.length; i++)
    {
	var lose_button = $('<button/>');
	lose_button.text(others[i]["name"])
	lose_button.click(
	    function(e)
	    {
		$(event.target).attr('disabled', 'disabled');
		puzzle["fails"]++;
		$("#fails").text("Errors: " + puzzle["fails"]);
	    });
	lose_buttons.push(lose_button);
    }
    var buttons = lose_buttons.concat([win_button]);
    shuffle(buttons);
    var box = $("#possibles");
    box.empty();
    for(var i = 0; i<buttons.length; i++)
    {
	box.append(buttons[i]);
    }

}

function new_puzzle(){
    $.ajax({
	url: "/random",
	success: function(data){
	    puzzle = data;

	    $("#name").text(puzzle["node"]["name"]);
	    let image = $("#image");
	    image.empty();
	    image.append("<img width='400px' src='" + puzzle["url"] + "'>");
	    puzzle["index"] = 0;
	    puzzle["fails"] = 0;
	    draw_buttons(0);
	},
    });
}



$(function(){
    new_puzzle();
});

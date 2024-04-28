var puzzle;

function build_name(node){
    if(only_magyar())
    {
	return node["alt_names"][1]
    }
    var res = node["name"]
    var alt_names = node["alt_names"]
    if (alt_names[0] != '' && alt_names[0] != node["name"])
    {
	res += ', ' + alt_names[0]
    }
    if (alt_names[1] != '' && alt_names[1] != node["name"] && alt_names[1] != alt_names[0])
    {
	res += ', ' + alt_names[1]
    }

    return res;
}

function only_magyar()
{
    return true;
}

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
    if(only_magyar() && ancestor["alt_names"][1] == "") return draw_buttons(index + 1);
    
    var others = puzzle["other_choices"][ancestor["tax_id"]];
    if(only_magyar()) others = others.filter((other) => other["alt_names"][1] != "");
    var win_button = $('<button/>');
    win_button.text(build_name(ancestor));
    win_button.click(function () { draw_buttons(index + 1); });
    lose_buttons = [];
    if(others.length > 5)
    {
	others = others.slice(0, 5);
    }

    for(var i = 0; i < others.length; i++)
    {
	var other = others[i];
	var lose_button = $('<button/>');
	lose_button.text(build_name(other))
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

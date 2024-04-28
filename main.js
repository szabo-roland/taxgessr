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

function draw_ui

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

function create_button(node, click_handler){
    let button = $('<button/>');
    button.text(build_name(node));
    button.click(click_handler);
    return button;
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
    win_button.click();
    let win_button = create_button(ancestor, () => draw_buttons(index + 1));

    let buttons = [win_button];

    if(others.length > 5)
    {
	others = others.slice(0, 5);
    }

    for(const other of others)
    {
	let lose_button = create_button(other, function(e)
	    {
		$(event.target).attr('disabled', 'disabled');
		puzzle["fails"]++;
		$("#fails").text("Errors: " + puzzle["fails"]);
	    });
	buttons.push(lose_button);
    }

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

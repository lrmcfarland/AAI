// Astronomy javascript

var astronomy = astronomy || {}; // namespace TODO starbug specific?

astronomy.setLocation = function() { // TODO set location

    console.log("astronomy.getLocation called");

    // TODO validation: error if length not 3, args not strings

    for (var i = 0; i < arguments.length; i++) {
	console.log("arg[" + i + "] = " + arguments[i]);
    }

    var latitude_id = arguments[0]; // closure for function
    var longitude_id = arguments[1];
    var timezone_id = arguments[2];

    if (!navigator.geolocation)
	console.log("Geolocation not supported"); // TODO raise error
    else
	console.log("Geolocation supported");

    navigator.geolocation.getCurrentPosition(function(pos) {

	var latitude = pos.coords.latitude;
	var longitude = pos.coords.longitude;

	console.log("latitude: " + latitude + ", longitude: " + longitude);

	document.getElementById(latitude_id).value = latitude;
	document.getElementById(longitude_id).value = longitude;

	// TODO floor < 0, ceiling > 0 better fit?
	document.getElementById(timezone_id).value = Math.round(longitude / 15); // assumes degrees

    });


};

// Astronomy javascript

var astronomy = astronomy || {}; // namespace TODO starbug specific?

astronomy.setLocation = function() { // TODO set location

    console.log("astronomy.setLocation called"); // debug?

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


    function success(pos) {

	var latitude = pos.coords.latitude;
	var longitude = pos.coords.longitude;

	console.log("latitude: " + latitude + ", longitude: " + longitude);

	document.getElementById(latitude_id).value = latitude;
	document.getElementById(longitude_id).value = longitude;

	// TODO floor < 0, ceiling > 0 better fit?

	timezone = Math.ceil(Math.round(longitude / 15)); // assumes degrees

	document.getElementById(timezone_id).value = timezone;

    };

    function error(err) {
	console.warn("Error: " + err.message);
	alert(err.message +
	      ".\nTODO I need set up starbug's CA certificate to support https." +
	      "\nManual entry is required at this time.");
    };

    navigator.geolocation.getCurrentPosition(success, error);

    // https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition

};

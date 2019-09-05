// aai javascript utilities
//
// a small example of a javascript module
// imported by base.html as <script type="text/javascript" src="{{ url_for('static', filename='aai.js') }}"></script>
//
// called by template/observer_location.html
//
// TODO copy in starbugdb

var aai = aai || {};

aai.setLocation = function() {
    // from https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition

    // closure
    var latitude_id = arguments[0];
    var longitude_id = arguments[1];
    var timezone_id = arguments[2];

    function success(pos) {

	var latitude = pos.coords.latitude;
	var longitude = pos.coords.longitude;

	document.getElementById(latitude_id).value = latitude;
	document.getElementById(longitude_id).value = longitude;

	aai.setTimezoneFromLocation(longitude_id, timezone_id);

    };

    function error(err) {
	console.error(err.message);
	alert(err.message + "\nManual entry is required at this time.");
    };

    if (!navigator.geolocation) {
	console.error("Geolocation not supported in this browser");
    } else {
	navigator.geolocation.getCurrentPosition(success, error);
    }

};


aai.setTimezoneFromLocation = function() {
    // from https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition

    // closure
    var longitude_id = arguments[0];
    var timezone_id = arguments[1];

    var longitude = document.getElementById(longitude_id).value;

    // TODO fractionial timezones, e.g. India +05:30, AU
    timezone = Math.ceil(Math.round(longitude / 15)); // assumes degrees


    if (timezone < 0) {

	document.getElementById(timezone_id).value = "-" + ("0" + -timezone).slice(-2) + ":00";

    } else {

	document.getElementById(timezone_id).value = "+" + ("0" + timezone).slice(-2) + ":00";

    };


};

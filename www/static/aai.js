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

	// TODO floor < 0, ceiling > 0 better for timezone?
	timezone = Math.ceil(Math.round(longitude / 15)); // assumes degrees

	document.getElementById(timezone_id).value = timezone;
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

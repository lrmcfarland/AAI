// aai javascript utilities
//
// a small example of a javascript module
// imported by base.html as <script type="text/javascript" src="{{ url_for('static', filename='aai.js') }}"></script>
//
//
// TODO copy in starbugdb?

var aai = aai || {};


aai.dd2dms = function () {
    // convert decimal degrees into a string of degrees:minutes:seconds for display

    let a_degree = arguments[0];

    let deg = parseInt(a_degree);
    let m = Math.abs((a_degree - deg) * 60);
    let min = Math.floor(m);
    let sec = (m - min) * 60;
    let sec_1 = sec.toFixed(1);

    let result = deg.toString() + ':' + ('0' + min.toString()).slice(-2) + ':' +  ('0' + sec_1.toString()).slice(-4)

    return result;

}


aai.getCurrentDateTime = function () {

    var now = new Date();

    var month_str = String(parseFloat(now.getMonth()) + 1);
    var date_str  = String(parseFloat(now.getDate()));

    var date_str = now.getFullYear() + "-" + month_str.padStart(2, "0") + "-" + date_str.padStart(2, "0");

    var hour_str = String(now.getHours());
    var min_str = String(now.getMinutes());
    var sec_str = String(now.getSeconds());

    var time_str = hour_str.padStart(2, "0") + ":" + min_str.padStart(2, "0") + ":" + sec_str.padStart(2, "0");

    return {date_str, time_str}

}


aai.setLocation = function() {

    // sets latitude and longitude values on ui using browser geolocation
    // from https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/getCurrentPosition

    // called by template/observer_location.html current location button

    let latitude_id = arguments[0];
    let longitude_id = arguments[1];
    let timezone_id = arguments[2];

    function success(pos) {

	let latitude = pos.coords.latitude;
	let longitude = pos.coords.longitude;

	document.getElementById(latitude_id).value = aai.dd2dms(latitude);
	document.getElementById(longitude_id).value = aai.dd2dms(longitude);

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

    // sets timezone from longitude displayed on ui

    let longitude_id = arguments[0];
    let timezone_id = arguments[1];

    let longitude = document.getElementById(longitude_id).value;

    // TODO fractionial timezones, e.g. India +05:30, AU
    timezone = Math.ceil(Math.round(parseFloat(longitude) / 15)); // assumes degrees

    if (timezone < 0) {

	document.getElementById(timezone_id).value = "-" + ("0" + -timezone).slice(-2) + ":00";

    } else {

	document.getElementById(timezone_id).value = "+" + ("0" + timezone).slice(-2) + ":00";

    };


};


aai.standardTimezone = function() {

    // Puts the timezone string in a standard format for Date
    // matches: +01:00, -02:00, 3, -4, +05:30
    // returns the timezone as a float and an hh:mm string

    const timezone_regex = new RegExp('(\\+|\\-){0,1}(\\d{1,2})(:(\\d\\d)){0,1}');

    let a_timezone = arguments[0];
    let timezone_elements = a_timezone.match(timezone_regex);

    // minutes
    let timezone_minutes_str = '00';
    let timezone_fractional_factor = 0.0; // for fractional time zones like Indias +05:30

    if (timezone_elements[4] != null) {
	timezone_minutes_str = timezone_elements[4];
	timezone_fractional_factor = parseFloat(timezone_elements[4])/60.0;
    }

    // hours
    let timezone_hours_str = '00';
    let timezone_factor = 1.0;

    if (timezone_elements[1] == '+') {
	timezone_hours_str = '+' + ('0' + timezone_elements[2]).slice(-2);

    } else if (timezone_elements[1] == '-') {
	timezone_hours_str = '-' + ('0' + timezone_elements[2]).slice(-2);

    } else {
	timezone_hours_str = '+' + ('0' + timezone_elements[2]).slice(-2);

    };


    timezone_factor = parseFloat(timezone_hours_str) + timezone_fractional_factor;

    let timezone_str = timezone_hours_str + ':' + timezone_minutes_str;

    return {timezone_factor, timezone_str};
};


aai.standardTime = function() {
    // Return timezone in ST adjusting for timezone and dst

    let a_date_str = arguments[0]; // str 2019-09-08
    let a_time_str = arguments[1]; // str 12:34:56.789
    let a_timezone_str = arguments[2]; // str -08:00
    let is_dst = arguments[3]; // bool


    let standard_time = {date_str: a_date_str,
			 time_str: a_time_str,
			 timezone_str: a_timezone_str}

    if (is_dst) {

	standard_time = aai.DST2ST(a_date_str,
				   a_time_str,
				   a_timezone_str);

    } else {

	std_tz = aai.standardTimezone(a_timezone_str);
	standard_time.timezone_str = std_tz.timezone_str;

    };


    return standard_time

};


aai.changeTime = function() {

    // add or subtract seconds from time value
    // returns date, time, timezone


    let a_date = arguments[0]; // str 2019-09-08
    let a_time = arguments[1]; // str 12:34:56.789
    let a_timezone = arguments[2]; // str -08:00
    let a_delta_time = parseFloat(arguments[3]); // float seconds

    std_timezone = aai.standardTimezone(a_timezone);

    let zulu_time = new Date(a_date
			     + "T" + a_time
			     + std_timezone.timezone_str);

    // fakes it by moving to zulu time but keeping the same timezone

    let local_time = new Date(zulu_time.getTime() + 3600000*std_timezone.timezone_factor + a_delta_time*1000);

    let date_str = local_time.toISOString().slice(0, 10);
    let time_str = local_time.toISOString().slice(11, -3); // rounds to 0.1 seconds
    let timezone_str = std_timezone.timezone_str;

    return {date_str, time_str, timezone_str};


};


aai.DST2ST = function() {

    // returns date, time, timezone in standard time for same in daylight saving time

    let a_date = arguments[0];
    let a_time = arguments[1];
    let a_timezone = arguments[2];

    return aai.changeTime(a_date, a_time, a_timezone, -60*60);

};


aai.ST2DST = function() {

    // returns date, time, timezone in daylight saving time for same in standard time

    let a_date = arguments[0];
    let a_time = arguments[1];
    let a_timezone = arguments[2];

    return aai.changeTime(a_date, a_time, a_timezone, 60*60);

};

// get current html name
var path = window.location.pathname;
var page = path.split("/").pop();
if(page == "") {
    page = "index.html";
}

// get agent name
var agent_name = get_request("agent");
if(agent_name != "") {
    console.log(page + ": acquire agent name - " + agent_name);
}

// adding getMax and getMin for Array
Array.prototype.getMin = function(attrib) {
    return this.reduce(function(prev, curr){ 
        return prev[attrib] < curr[attrib] ? prev : curr; 
    });
}

Array.prototype.getMax = function(attrib) {
    return this.reduce(function(prev, curr){ 
        return prev[attrib] > curr[attrib] ? prev : curr; 
    });
}

// generate a hash code for string
String.prototype.hashCode = function() {
  var hash = 0, i, chr;
  if (this.length === 0) return hash;
  for (i = 0; i < this.length; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

// This is a funtion to handle GET request
function get_request(name) {
    if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
    return decodeURIComponent(name[1]);
}

// find min or max value
// finder(Math.max, dt.status, function(x) { return parseInt(x.code); });
function finder(cmp, arr, getter) {
    var val = getter(arr[0]);
    for(var i = 1; i < arr.length; i++) {
        val = cmp(val, getter(arr[i]));
    }
    return val;
}

// find key in object and return obj
// var test = {'level1':{'level2':{'level3':'level3'}} };
// checkNested(test, 'level1', 'level2', 'level3');

function checkNested(obj /*, level1, level2, ... levelN*/) {
    var args = Array.prototype.slice.call(arguments, 1);

    for (var i = 0; i < args.length; i++) {
        if (!obj || !obj.hasOwnProperty(args[i])) {
            return false;
        }
        obj = obj[args[i]];
    }
    return obj;
}

// This is used to translate data ( Shako's old format )
function translate_obj( data ) {
    var table_data = {"data": []};
    for (var type_key in data) {
        var timestamp_data = data[type_key];

        for (var timestamp in timestamp_data) {
            var cmd_data = timestamp_data[timestamp];

            for (var cmd in cmd_data) {
                var status_data = cmd_data[cmd];
                console.log(page + ": parsing data from \"" + type_key + "-" + timestamp + "-" + cmd + "\"");

                // getting all the status data sets
                additional_data = [];
                for (var status in status_data) {
                    // adding code in each status object
                    status_data[status]["code"] = status;
                    // storing status into an array so that I can put it in dictionary later
                    additional_data.push(status_data[status]);
                }

                // push into total data set
                data_set = {"type": type_key, "cmd": cmd, "start_ts": timestamp, "status": additional_data};
                table_data["data"].push(data_set);
            }

        }
    }
    return table_data;
}

// Find deep path in object
function deepFind(obj, path) {
  var paths = path.split('.')
    , current = obj
    , i;

  for (i = 0; i < paths.length; ++i) {
    if (current[paths[i]] == undefined) {
      return undefined;
    } else {
      current = current[paths[i]];
    }
  }
  return current;
}

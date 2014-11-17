
var BASE = "http://127.0.0.1:5000/people";

function request(verb, endpoint, obj, callback) {
    print("Request: "
          + verb
          + " "
          + BASE
          + (endpoint ? "/" + endpoint : ""))

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        print("xhr: on ready state change: " + xhr.readyState);
        if (xhr.readyState === xhr.DONE) {
            if (callback) {
                // console.log("responseText: ", xhr.responseText.toString());
                var res = JSON.parse(xhr.responseText.toString());
                callback(res);
            }
        }
    }

    xhr.open(verb, BASE + (endpoint ? "/" + endpoint : ""));
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "application/json");
    var data = obj ? JSON.stringify(obj) : ""
    xhr.send(data)
}

function get_people(callback) {
    // GET http://127.0.0.1:5000/people
    request('GET', null, null, callback)
}

function create_person(entry, callback) {
    // POST http://127.0.0.1:5000/people
    request('POST', null, entry, callback)
}

function get_person(name, callback) {
    // GET http://127.0.0.1:5000/people/<name>
    request('GET', name, null, callback)
}

function update_person(name, entry, callback) {
    // PUT http://127.0.0.1:5000/people/<name>
    request('PUT', name, entry, callback)
}

function delete_person(name, callback) {
    // DELETE http://127.0.0.1:5000/people/<name>
    request('DELETE', name, null, callback)
}
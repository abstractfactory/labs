function loadModel(model) {
    // Create a request, and tell it where the JSON is
    var req = new XMLHttpRequest();

    // Tell the request to go and get the JSON
    req.open("GET", location, true);
    req.send();

    // Wait until the readyState is 4, which means it's ready.
    req.onreadystatechange = function () {
        if (req.readyState == 4) {
            // Append each item to the ListModel
            JSON.parse(req.responseText).forEach(function (item) {
                model.append(item);
            });
        }
    };
}

"use strict";

var express = require('express'),
    api     = require('./api'),
    app     = express();

app
    .use(express.static('./public'))
    .use('/api', api)
    .get('*', function (req, res) {
        // Unused variable is ok, and __dirname is a global
        res.sendFile('public/main.html', {'root': __dirname});
    })
    .listen(3000);

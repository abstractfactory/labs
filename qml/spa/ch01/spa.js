"use strict";
/*global spaSliderLoader */

var configMap = {
        extended_height: 434,
        extended_title: "Click to retract",
        retracted_height: 16,
        retracted_title: "Click to extend",
        template_url: "SpaSlider.qml"
    },
    toggleSlider,
    onClickSlider,
    initModule;

/*
* Extend or retract slider
*/
toggleSlider = function () {
    var slider_height = spaSliderLoader.item.height;

    if (slider_height === configMap.retracted_height) {
        spaSliderLoader.item.height = configMap.extended_height;
    } else {
        spaSliderLoader.item.height = configMap.retracted_height;
    }
};

/**
* Event handler for clicks
*/
onClickSlider = function () {
    toggleSlider();
};

initModule = function () {
    spaSliderLoader.source = configMap.template_url;
    spaSliderLoader.item.clicked.connect(onClickSlider);
};

console.log("Hello");

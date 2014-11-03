// Unless a variable is declared somewhere, using it
// causes the Javascript engine to stop executing code
//  i.e. to crash.
// 
// By declaring it, even without giving it a value, we
// save the engine.

"use strict";

function continues() {
    console.log(prisoner);
    var prisoner;
}

function breaks() {
    console.log(prisoner);
}

continues();
// breaks();
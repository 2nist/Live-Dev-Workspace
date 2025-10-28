inlets = 1;
outlets = 1;

// Called when OSC data arrives
function list() {
  // args: [type, ...data]
  var type = arguments[0];
  if (type === "chord") {
    // Play chord notes
    for (var i = 1; i < arguments.length; i++) {
      outlet(0, [arguments[i], 100]);
    }
  } else if (type === "scale") {
    // Store scale for filtering
    // ...your code here...
  }
}

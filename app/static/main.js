var PointCalibrate = 0;
var CalibrationPoints = {};

function showPrototype() {
  document.getElementById("figma-prototype").style.display = "block";
}

document.addEventListener("DOMContentLoaded", function () {
  var myModal = new bootstrap.Modal(document.getElementById("modal-ayuda"));
  myModal.show();

  // Agrega un evento de clic a todos los elementos con la clase 'Calibration'.
  document.querySelectorAll(".Calibration").forEach((i) => {
    // Cuando se hace clic en un elemento con la clase 'Calibration', se llama a la función calPointClick
    // pasando el elemento clicado como argumento.
    i.addEventListener("click", () => {
      calPointClick(i);
    });
  });
  ShowCalibrationPoint();

  // Manejar el clic en el botón "Entendido"
  document.getElementById("btn-entendido").addEventListener("click", function () {
    myModal.hide(); // Cierra el modal
  });
});



/**
 * Show the Calibration Points
 */
function ShowCalibrationPoint() {
  document.querySelectorAll(".Calibration").forEach((i) => {
    i.style.removeProperty("display");
  });
  // initially hides the middle button
  document.getElementById("Pt5").style.setProperty("display", "none");
}

var calibrated = false;

function calPointClick(node) {
  const id = node.id;

  if (!CalibrationPoints[id]) {
    // initialises if not done
    CalibrationPoints[id] = 0;
  }
  CalibrationPoints[id]++; // increments values

  if (CalibrationPoints[id] == 5) {
    //only turn to yellow after 5 clicks
    node.style.setProperty("background-color", "yellow");
    node.setAttribute("disabled", "disabled");
    PointCalibrate++;
  } else if (CalibrationPoints[id] < 5) {
    //Gradually increase the opacity of calibration points when click to give some indication to user.
    var opacity = 0.2 * CalibrationPoints[id] + 0.2;
    node.style.setProperty("opacity", opacity);
  }

  //Show the middle calibration point after all other points have been clicked.
  if (PointCalibrate == 8) {
    document.getElementById("Pt5").style.removeProperty("display");
  }

  if (PointCalibrate >= 9) {
    // last point is calibrated
    // grab every element in Calibration class and hide them except the middle point.
    document.querySelectorAll(".Calibration").forEach((i) => {
      i.style.setProperty("display", "none");
    });

    calibrated = true;

    // showPrototype();
  }
}

/*
 * Sets store_points to true, so all the occuring prediction
 * points are stored
 */
function store_points_variable() {
  webgazer.params.storingPoints = true;
}
/*
 * Sets store_points to false, so prediction points aren't
 * stored any more
 */
function stop_storing_points_variable() {
  webgazer.params.storingPoints = false;
}

// -----------------------------
window.onload = async function () {
  //start the webgazer tracker
  await webgazer
    .setRegression("ridge") /* currently must set regression and tracker */
    .setTracker('clmtrackr')
    .saveDataAcrossSessions(true)
    .begin();
  webgazer
    .showVideoPreview(true) /* shows all video previews */
    .showPredictionPoints(
      true
    ) /* shows a square every 100 milliseconds where current prediction is */
    .applyKalmanFilter(
      true
    ); /* Kalman Filter defaults to on. Can be toggled by user. */

  //Set up the webgazer video feedback.
  var setup = function () {
    //Set up the main canvas. The main canvas is used to calibrate the webgazer.
    var canvas = document.getElementById("plotting_canvas");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.position = "fixed";
  };
  setup();
};

// Set to true if you want to save the data even if you reload the page.
window.saveDataAcrossSessions = true;

window.onbeforeunload = function () {
  webgazer.end();
};

/**
 * Restart the calibration process by clearing the local storage and reseting the calibration point
 */
function Restart() {
  webgazer.clearData();
  ClearCalibration();
  PopUpInstruction();
}

function isCalibrated() {
  return calibrated;
}

/**
 * Saving data
 */
const urlParams = new URLSearchParams(window.location.search);
const id = urlParams.get("id");

fetch("/config")
  .then((response) => response.json())
  .then((config) => {
    const imgElement = document.getElementById("img_interes");
    console.log(config.img_path);
    imgElement.src = config.img_path;
  })
  .catch((error) =>
    console.error("Error al cargar el archivo config.json:", error)
  );

function enviarPuntos(puntos) {
  fetch("/guardar-puntos", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ puntos: puntos, id: parseInt(id, 10) }),
  })
    .then((response) => response.text())
    .then((result) => {
      console.log(result);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// // Obtener referencia al iframe
// const iframe = document.getElementById("prototype");

// // Función para enviar un punto (x, y)
// function enviarPuntoIframe(x, y) {
//   const punto = { x, y }; // Crear el objeto con las coordenadas
//   iframe.contentWindow.postMessage(punto, "http://127.0.0.1:5500"); // Enviar el mensaje al iframe
// }

let points = [];
let mouse_position = { x: 0, y: 0 }; // Define mouse_position as an object

document.addEventListener("mousemove", (event) => {
  if (isCalibrated()) {
    mouse_position.x = event.clientX;
    mouse_position.y = event.clientY;
  }
});

// Inicia WebGazer.js y establece el GazeListener
document.addEventListener("DOMContentLoaded", function () {
  webgazer
    .setGazeListener(function (data, elapsedTime) {
      if (data == null) {
        return;
      }
      webgazer.util.bound(data);

      if (isCalibrated()) {
        var xprediction = data.x; // Coordenadas x relativas al viewport
        var yprediction = data.y; // Coordenadas y relativas al viewport

      // Add the current timestamp to each point
      const currentTimestamp = new Date().toISOString();

      points.push({
        fecha: currentTimestamp, // Add the timestamp here
        gaze: {
          x: xprediction,
          y: yprediction,
        },
        mouse: {
          x: mouse_position.x,
          y: mouse_position.y,
        },
      });

        if (points.length == 20) {
          console.log("Enviando puntos...");
          enviarPuntos(points);
          points = [];
        }
      }
    })
    .begin();
});
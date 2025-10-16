/**
 * Script para la visualización de resultados con mapa de calor
 */

// Obtener parámetros de la URL
const urlParams = new URLSearchParams(window.location.search);
const id = urlParams.get('id');

/**
 * Descarga el archivo de puntos de seguimiento
 */
function descargarArchivo() {
  window.location.href = `/api/download-points?id=${id}`;
}

/**
 * Descarga el archivo de tareas
 */
function descargarTareas() {
  window.location.href = `/api/download-tasklogs?id=${id}`;
}

// Event listeners para los botones de descarga
document.getElementById('btn-descarga-tasks').addEventListener('click', function() {
  descargarTareas();
});

document.getElementById('btn-descarga').addEventListener('click', function() {
  descargarArchivo();
});

/**
 * Inicialización del mapa de calor al cargar la página
 */
window.onload = function() {
  // Los puntos se pasan desde el template
  var puntosOriginales = window.puntosData;

  fetch("/api/config")
    .then((response) => response.json())
    .then((config) => {
      const prototypeUrl = config.url_path;
      const imgPath = config.img_path;

      if (
        (!prototypeUrl || prototypeUrl === "null") &&
        (!imgPath || imgPath === "null")
      ) {
        console.error(
          "Error: Ambos valores son nulos. Debe configurarse 'prototype_url' o 'img_path'."
        );
        alert(
          "Error: No se ha configurado correctamente el prototipo o la imagen."
        );
        return;
      }

      if (prototypeUrl && prototypeUrl !== "null") {
        console.log(prototypeUrl);
        const iframe = document.getElementById("prototype");
        iframe.src = prototypeUrl;
        iframe.style.display = "block";
      } else if (imgPath && imgPath !== "null") {
        const imgElement = document.getElementById("img_interes");
        imgElement.src = imgPath;
        imgElement.style.display = "block";
      }

      // Normalizar puntos para el mapa de calor
      var puntos = puntosOriginales.map(punto => ({
        x: punto.x + Math.abs(Math.min(0, punto.x)),
        y: punto.y + Math.abs(Math.min(0, punto.y))
      }));

      var data = {
        max: 10,
        min: 0,
        data: puntos.map(punto => ({
          x: parseFloat(punto.x),
          y: parseFloat(punto.y),
          value: 5
        }))
      };

      console.log('Puntos:', puntos);
      console.log('Configurando heatmap con los siguientes datos:', data);

      // Crear instancia del mapa de calor
      var heatmapInstance = h337.create({
        container: document.querySelector('.heatmap')
      });
      heatmapInstance.setData(data);
      heatmapInstance.repaint();
    })
    .catch((error) =>
      console.error("Error al cargar la configuración desde /api/config:", error)
    );
};

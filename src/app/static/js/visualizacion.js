function getSujetoIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

async function cargarDatos() {
    try {
        const sujetoId = getSujetoIdFromUrl();
        if (!sujetoId) {
            console.error("No se especificó el parámetro ?id en la URL");
            return;
        }

        const response = await fetch(`/api/get-user-points?id=${sujetoId}`);
        if (!response.ok) {
            throw new Error("Error al obtener datos del API");
        }
        const data = await response.json();

        console.log("Datos recibidos:", data);

        if (!data.points || data.points.length === 0) {
            console.warn("No se encontraron puntos para este sujeto");
            return;
        }

        // === Animación Mouse ===
        let mouseFrames = data.points.map((p, i) => ({
            name: i.toString(),
            data: [{
                x: data.points.slice(0, i + 1).map(q => q.x_mouse),
                y: data.points.slice(0, i + 1).map(q => q.y_mouse),
                mode: "markers+lines",
                marker: { size: 6, color: "blue" }
            }]
        }));

        let mouseLayout = {
            title: {
                text: `Movimiento del Mouse (Sujeto ${sujetoId})`,
                font: { size: 18 },
                x: 0.5,
                xanchor: 'center'
            },
            xaxis: { range: [0, 1920], title: "X", fixedrange: true },
            yaxis: { range: [1080, 0], title: "Y", scaleanchor: "x", fixedrange: true },
            width: 700,
            height: 500,
            updatemenus: [{
                type: "buttons",
                showactive: false,
                buttons: [
                    {
                        label: "▶️ Play",
                        method: "animate",
                        args: [null, {
                            fromcurrent: true,
                            frame: { duration: 200, redraw: true },
                            transition: { duration: 100 }
                        }]
                    },
                    {
                        label: "⏸ Pause",
                        method: "animate",
                        args: [[null], {
                            mode: "immediate",
                            frame: { duration: 0 },
                            transition: { duration: 0 }
                        }]
                    }
                ]
            }],
            sliders: [{
                steps: mouseFrames.map(f => ({
                    label: f.name,
                    method: "animate",
                    args: [[f.name], {
                        mode: "immediate",
                        frame: { duration: 0, redraw: true },
                        transition: { duration: 0 }
                    }]
                }))
            }]
        };

        Plotly.newPlot("mouse-plot", [{
            x: [data.points[0].x_mouse],
            y: [data.points[0].y_mouse],
            mode: "markers+lines",
            marker: { size: 6, color: "blue" }
        }], mouseLayout).then(() => {
            Plotly.addFrames("mouse-plot", mouseFrames);
        });

        // === Animación Gaze ===
        let gazeFrames = data.points.map((p, i) => ({
            name: i.toString(),
            data: [{
                x: data.points.slice(0, i + 1).map(q => q.x_gaze),
                y: data.points.slice(0, i + 1).map(q => q.y_gaze),
                mode: "markers+lines",
                marker: { size: 6, color: "red" }
            }]
        }));

        let gazeLayout = {
            title: {
                text: `Movimiento de la Mirada (Sujeto ${sujetoId})`,
                font: { size: 18 },
                x: 0.5,
                xanchor: 'center'
            },
            xaxis: { range: [0, 1920], title: "X" ,fixedrange: true},
            yaxis: { range: [1080, 0], title: "Y", scaleanchor: "x", fixedrange: true },
            width: 700,
            height: 500,
            updatemenus: [{
                type: "buttons",
                showactive: false,
                buttons: [
                    {
                        label: "▶️ Play",
                        method: "animate",
                        args: [null, {
                            fromcurrent: true,
                            frame: { duration: 200, redraw: true },
                            transition: { duration: 100 }
                        }]
                    },
                    {
                        label: "⏸ Pause",
                        method: "animate",
                        args: [[null], {
                            mode: "immediate",
                            frame: { duration: 0 },
                            transition: { duration: 0 }
                        }]
                    }
                ]
            }],
            sliders: [{
                steps: gazeFrames.map(f => ({
                    label: f.name,
                    method: "animate",
                    args: [[f.name], {
                        mode: "immediate",
                        frame: { duration: 0, redraw: true },
                        transition: { duration: 0 }
                    }]
                }))
            }]
        };

        Plotly.newPlot("gaze-plot", [{
            x: [data.points[0].x_gaze],
            y: [data.points[0].y_gaze],
            mode: "markers+lines",
            marker: { size: 6, color: "red" }
        }], gazeLayout).then(() => {
            Plotly.addFrames("gaze-plot", gazeFrames);
        });

    } catch (error) {
        console.error("Error cargando datos:", error);
    }
}

function descargarGrafico(plotId, formato) {
    const sujetoId = getSujetoIdFromUrl();
    const plotType = plotId === 'mouse-plot' ? 'mouse' : 'gaze';
    const filename = `${plotType}_sujeto_${sujetoId}`;
    
    const config = {
        format: formato,
        filename: filename,
        width: 1400,
        height: 1000,
        scale: 2 // Higher resolution
    };
    
    Plotly.downloadImage(plotId, config);
}

async function descargarAnimacion(plotId, formato) {
    const sujetoId = getSujetoIdFromUrl();
    const plotType = plotId === 'mouse-plot' ? 'mouse' : 'gaze';
    const filename = `${plotType}_sujeto_${sujetoId}_animacion`;
    
    const btnId = `${plotType}-${formato}-btn`;
    const btn = document.getElementById(btnId);
    const originalText = btn.textContent;
    btn.disabled = true;
    
    try {
        if (formato === 'webm') {
            btn.textContent = '⏳ Grabando video...';
            await descargarComoWebM(plotId, filename, btn);
        }
        btn.disabled = false;
        btn.textContent = originalText;
    } catch (error) {
        console.error('Error al grabar animación:', error);
        alert('Error al generar la animación: ' + error.message);
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function descargarComoWebM(plotId, filename, btn) {
    const plotElement = document.getElementById(plotId);
    
    // Crear un canvas para la grabación
    const canvas = document.createElement('canvas');
    canvas.width = 700;
    canvas.height = 500;
    const ctx = canvas.getContext('2d');
    
    const stream = canvas.captureStream(30); // 30 fps
    const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8',
        videoBitsPerSecond: 2500000
    });
    
    const chunks = [];
    
    mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
            chunks.push(e.data);
        }
    };
    
    return new Promise((resolve, reject) => {
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${filename}.webm`;
            a.click();
            URL.revokeObjectURL(url);
            resolve();
        };
        
        mediaRecorder.onerror = reject;
        
        // Iniciar grabación
        mediaRecorder.start();
        
        // Función para capturar frames
        let frameIndex = 0;
        const totalFrames = 50;
        const frameInterval = setInterval(async () => {
            if (frameIndex >= totalFrames) {
                clearInterval(frameInterval);
                if (btn) {
                    btn.textContent = '⏳ Finalizando...';
                }
                setTimeout(() => {
                    mediaRecorder.stop();
                }, 500);
                return;
            }
            
            if (btn) {
                btn.textContent = `⏳ Grabando ${frameIndex + 1}/${totalFrames}...`;
            }
            
            // Animar al siguiente frame
            await Plotly.animate(plotId, [frameIndex.toString()], {
                transition: { duration: 0 },
                frame: { duration: 0, redraw: true }
            });
            
            // Capturar imagen del plot
            const imgData = await Plotly.toImage(plotId, {
                format: 'png',
                width: 700,
                height: 500
            });
            
            // Dibujar en el canvas
            const img = new Image();
            img.onload = () => {
                ctx.drawImage(img, 0, 0);
            };
            img.src = imgData;
            
            frameIndex++;
        }, 200); // 200ms por frame (5 fps)
    });
}

document.addEventListener("DOMContentLoaded", cargarDatos);

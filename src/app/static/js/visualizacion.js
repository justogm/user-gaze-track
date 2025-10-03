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
            yaxis: { range: [0, 1080], title: "Y", scaleanchor: "x", fixedrange: true },
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
            yaxis: { range: [0, 1080], title: "Y", scaleanchor: "x", fixedrange: true },
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

document.addEventListener("DOMContentLoaded", cargarDatos);

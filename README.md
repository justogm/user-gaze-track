# User Gaze Tracking Tool for Prototypes

This web application uses Flask as the backend to handle data entry and WebGazer.js in the frontend to perform user gaze tracking. The basic application flow is as follows:

1. **Home Page (/):** Contains a data entry form. Users should fill the form and click "Submit" to proceed.

2. **Gaze Tracking Page:** After submitting the form, you will be redirected to a page where gaze tracking starts using WebGazer.js. The page includes a calibration phase with a series of buttons and then displays a Figma prototype to record the user's gaze behavior. The collected data is stored in a SQLite database (this can be changed later; SQLite was chosen for convenience during development).

3. **Subjects Page (/sujetos):** View the subjects stored in the database. You can access each subject's details and gaze tracking data.

4. **Results Page for a subject (/resultados?id={sujeto}):** View the gaze heatmap for a subject and download their data as CSV.

## Uso del Proyecto

### 1. Clona este repositorio

```bash
git clone https://github.com/justogm/user-gaze-track.git
cd user-gaze-track
```

### 2. Run the tool

```bash
python run.py
```

## Importante

> [!CAUTION]
> Esta herramienta está en desarrollo y está pensada para entornos controlados, aún presenta severas vulnerabilidades para su distribución. Se recomienda no utilizarla en entornos de producción.

## Tecnologías relevantes

- [Flask](https://flask.palletsprojects.com/en/3.0.x/)
- [WebGazer.js](https://webgazer.cs.brown.edu/)
- [heatmap.js](https://www.patrick-wied.at/static/heatmapjs/)
- [SQLite](https://www.sqlite.org/index.html)

## Capturas de pantalla

### 1. Ingreso de datos

Puede ser modificado de acuerdo a las variables que se consideren relevantes.

![Data Entry](assets/readme/data-entry.png)

### 2. Calibration and instructions

![Calibration and instructions](assets/readme/instrucciones-y-calibracion.png)

*The calibration instructions image is provided by the module; consider creating a translated version if needed.*

### 3. Prototype presentation

![Prototype presentation](assets/readme/prototipo-figma.png)

## TODO

- [ ] Evaluate module behavior when the prototype is in fullscreen mode.
- [ ] Explore alternatives for prototype presentation.
- [x] Make it easier to change the prototype instead of leaving it hardcoded.
  - A configuration file was created; see the [configuration section](#4-configure-the-tool).
- [x] Develop a parallel app for accessing and manipulating generated data.
  - The route `/sujetos` was developed

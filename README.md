# Herramienta de Seguimiento de Interacciones del Usuario con Prototipos

Esta aplicación web utiliza Flask como backend para gestionar la entrada de datos y WebGazer.js en el frontend para realizar el seguimiento de la vista del usuario. El flujo básico de la aplicación es el siguiente:

1. **Página de Inicio (/):** Aquí encontrarás un formulario de entrada de datos. Los usuarios deben completar el formulario y hacer clic en "Submit" para avanzar.

2. **Página de Gaze Tracking:** Después de enviar el formulario, serás redirigido a una página donde se iniciará el seguimiento de la vista mediante WebGazer.js. La página pasará por una fase de calibración con una serie de botones y luego mostrará un prototipo de Figma para registrar el comportamiento de la vista del usuario. Los datos obtenidos se irán registrando en una base de datos de SQLite (puede luego cambiarse, esta fue seleccioanda por conveniencia para el desarrollo).

## Configuración del Proyecto

1. Clona este repositorio:

    ```bash
    git clone https://github.com/justogm/user-gaze-track.git
    cd user-gaze-track
    ```

2. Instala los requerimientos
    ```bash
    pip install -r requirements.txt
    ```

3. Generar certificados
Para poder utilizar el módulo de gaze tracking debe soportar https. Por ello, deben crearse las credenciales para que funcione correctamente.

    ```bash
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    ```

Este comando realizará una serie de preguntas y finalmente creará los archivos *cert.pem* y *key.pem* que utilizará Flask.

4. Correr la herramienta
    ```bash
    python app.py
    ```

## Tecnologías relevantes
- [Flask](https://flask.palletsprojects.com/en/3.0.x/)
- [WebGazer.js](https://webgazer.cs.brown.edu/)
- [SQLite](https://www.sqlite.org/index.html)

## Captura de pantalla
1. Ingreso de datos
Puede ser modificado de acuerdo a las variables que se consideren relevantes.

![Data Entry](assets/readme/data-entry.png)

2. Etapa de calibración e instrucciones

![Calibración e instrucciones](assets/readme/instrucciones-y-calibracion.png)

*La imagen de instrucciones para la calibración es la proporcionada por el módulo, sería conveniente crear una que se encuentre traducida al español.*

3. Presentación del prototipo

## TODO
-[] Evaluar comportamiento del modulo en caso de tener el prototipo en pantalla completa.
-[] Analizar alternativas para la presentación del prototipo.
-[] Facilitar el cambio del prototipo, no dejarlo hardcodeado.
-[] Desarrollar una app paralela para el acceso a los datos generados y su manipulación.
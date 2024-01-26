# Herramienta de Seguimiento de Interacciones del Usuario con Prototipos

Esta aplicación web utiliza Flask como backend para gestionar la entrada de datos y WebGazer.js en el frontend para realizar el seguimiento de la vista del usuario. El flujo básico de la aplicación es el siguiente:

1. **Página de Inicio (/):** Aquí encontrarás un formulario de entrada de datos. Los usuarios deben completar el formulario y hacer clic en "Submit" para avanzar.

2. **Página de Gaze Tracking:** Después de enviar el formulario, serás redirigido a una página donde se iniciará el seguimiento de la vista mediante WebGazer.js. La página pasará por una fase de calibración con una serie de botones y luego mostrará un prototipo de Figma para registrar el comportamiento de la vista del usuario.

## Requisitos

- Python 3.x
- Flask 

## Configuración del Proyecto

1. Clona este repositorio:

```bash
git clone https://tu-repositorio.git
cd tu-repositorio
```

2. Instala los requerimientos
```bash
pip install -r requirements.txt
```

3. Corre la herramienta
```bash
python app.py
```

## Tech
- [Flask](https://flask.palletsprojects.com/en/3.0.x/)
- [WebGazer.js](https://webgazer.cs.brown.edu/)

## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)
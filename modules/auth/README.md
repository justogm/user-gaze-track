# Módulo de autenticación de usuario
Este proyecto consiste en un módulo de autenticación de usuario.

## Descripción

El repositorio tiene dos ramas. En la rama ```main``` se lleva el desarrollo y la rama core-only contiene la última versión estable para usar.
 
## Dependencias

Las dependencias generales de este proyecto que están en ```deps/requirements.txt``` corresponde al funcionamiento integral de las aplicaciones de prueba. Las dependendencias específicas de la parte que se importa desde otros proyectos está en ```modules/requirements.txt```.

---

## Flujo de trabajo en este repo
1. Se trabaja en la rama main
2. Cuando esté listo para usar, se actualiza la rama core-only
```bash
   # Cambiar a la rama core-only
   git checkout core-only

   # Limpiar rama core-only para copiar contenido de modules de la rama main
   git rm -rf .

   # Traer desde main el contenido de la carpeta modules, reemplazando contenido previo
   git checkout main -- modules/ && mv modules/* ./ && rmdir modules
```
3. Hacer commit y push
```bash
   git add modules/
   git commit -m "Actualización core-only desde main"
   git push origin core-only
```

## Cómo usarlo en mis proyectos
Debes colocar el contenido de modules de este proyecto en la carperta modules de tu proyecto --que lo llamaremos **mi_proyecto**--. La estructura de carpetas de mi_proyecto luego de integrar el módulo debería quedar así:
   ```bash
   mi_proyecto/
   │
   ├── modules/
   │ └── auth/ # Código de autenticación proveniente de este repo (rama core-only)
   ├── tests/ 
   ├── otras/  
   ├── carpetas/  
   └── main.py # Punto de entrada de mi_proyecto
```
### Pasos para integrar el repositorio

1. Posicionarse en el repo "mi_proyecto"
   ```bash
   cd /ruta/a/mi_proyecto
   ```
2. Agregar el modulo de autenticación
   ```bash 
   git remote add auth_repo https://github.com/FIUNER-LICA/autentication-module.git
   ```
3. Integrar el código de la rama core-only en la carpeta modules/auth:
   ```bash
   git subtree add --prefix=modules/auth auth_repo core-only --squash
   ```
4. Verificar la estructura
   ```bash
   tree -L 2
   ```
### Cómo actualizar mi_proyecto cuando el módulo de autenticación tenga nueva versión
```bash
   git subtree pull --prefix=modules/auth auth_repo core-only --squash
```

## 🔎Pruebas y Verificación

📌 Ejecución de pruebas automatizadas:
_Si se tiene tests implementados, explicar qué prueban y cómo ejecutarlos._

📌 Pruebas manuales:
_Si se tiene pruebas manuales, describir los pasos para revisar que todo funcione como debería._

---

## 🐞Errores comunes y cómo solucionarlos 

_Agregar aquí cualquier error típico que puede ocurrir durante la ejecución del proyecto y su posible solución_

---

## 👥 **Cómo Contribuir**

_Si este proyecto es colaborativo, explicar cómo otros pueden contribuir._

---

## 📜 **Licencia**

_Si el proyecto tiene una licencia, incluirla aquí (ejemplo: MIT, GPL, Apache)._

---
## 🙎‍♀️🙎‍♂️Contacto

_Indicar integrantes del proyecto y contacto si corresponde_

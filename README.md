# Head Rider — Documentación de Interfaz y Modos de Juego

**Head Rider** es un videojuego arcade de carreras y esquive en **un solo jugador** desarrollado en Python con Pygame. Su interfaz combina una estética *pixel art* nocturna en el menú principal con pantallas funcionales enfocadas en la calibración de la cámara y el control de la moto mediante el seguimiento de la **nariz**.

> **Créditos:** Creado por Juan Ceballos y Angel Rodriguez.

---

## 1. Menú Principal

![Menú Principal de Head Rider](assets/captura_menu.png)

La ventana principal (`400x600`) presenta el título **Head Rider** sobre un escenario urbano nocturno en *pixel art* con motos en carretera, un pie de página con los créditos y tres botones interactivos con efecto *hover*:

* **INICIAR:** Activa el control por cámara/nariz para la partida, inicia el modo de juego en **1 solo jugador** y cambia la música de espera a la pista de la carrera.
* **INSTRUCCIONES:** Abre la pantalla de guía y prueba de cámara, donde se verifica la disponibilidad de la cámara y se calibra el punto neutral de seguimiento (la punta de la nariz).
* **SALIR:** Cierra la aplicación y detiene los procesos y el audio de forma completa.

---

## 2. Pantalla de Instrucciones y Calibración

![Pantalla de Instrucciones y Cámara](assets/captura_instrucciones.png)

Esta vista permite preparar el control facial antes de entrar a la pista:

* **Guía en pantalla:** Explica que la moto se controla moviendo la **nariz** (izquierda, derecha, arriba y abajo), indica el uso de la tecla `C` para recalibrar el centro neutral y muestra `W A S D` como control alternativo por teclado.
* **Visor de cámara en vivo:** Muestra la captura de la cámara dentro de la interfaz con indicadores visuales:
  * Punto verde sobre la nariz detectada.
  * Recuadro de zona muerta alrededor del centro calibrado.
  * Avisos de estado en la esquina superior izquierda (por ejemplo, *"Calibrando... mira al frente"* o *"No se detecta tu cara"* cuando no hay rostro visible) y recordatorio *"C = recalibrar"* en la parte inferior.
* **RECALIBRAR (C):** Reinicia las muestras de calibración para volver a fijar la posición neutral de la nariz.
* **VOLVER:** Regresa al **Menú Principal** (también accesible con la tecla `ESC`).

---

## 3. Modo de Juego (Un Solo Jugador)

El juego está diseñado exclusivamente para **1 jugador** en una pista vertical con tráfico en movimiento:

* **Conducción:** Guiar la moto esquivando los carros que avanzan en los carriles, utilizando el movimiento de la nariz como control principal o las teclas `W`, `A`, `S`, `D` como respaldo.
* **Progresión y puntajes:** El puntaje aumenta con el tiempo de supervivencia en la partida, mientras el tráfico incrementa gradualmente su velocidad y el escenario rota periódicamente (o manualmente con `ESPACIO`).
* **Fin de partida:** Al chocar contra un vehículo enemigo, finaliza la ronda, se muestra el puntaje obtenido y se ofrece la opción de volver al menú.

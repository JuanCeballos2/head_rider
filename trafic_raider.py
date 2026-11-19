import pygame
import random
import os
import threading
import time
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from motos import Moto
from carros import Carro, Generador
from escenarios import Escenario


# Rutas relativas: carpeta `assets` junto al archivo `trafic_raider.py`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Inicialización de Pygame y configuración de la ventana
pygame.init()
Ancho = 400
Alto = 600
Ventana = pygame.display.set_mode((Ancho, Alto))
pygame.display.set_caption("Head Rider")
RELOJ = pygame.time.Clock()
FPS = 60

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)

# ---------------------------------------------------------------------------
# Ajustes del control por cabeza (puedes tocarlos para afinar la sensibilidad)
# ---------------------------------------------------------------------------
INDICE_CAMARA = 0        # Cambia a 1 si tienes varias cámaras
ZONA_MUERTA_X = 0.03     # Cuánto puedes mover la cabeza sin que la moto reaccione
ZONA_MUERTA_Y = 0.025
RANGO_X = 0.10           # Desplazamiento (desde la zona muerta) para velocidad máxima
RANGO_Y = 0.07
SUAVIZADO = 0.5          # 0 a 1: más alto = responde más rápido, más bajo = más suave
MUESTRAS_CALIBRACION = 20

# Modelo de MediaPipe (API nueva). Se descarga automáticamente la primera vez.
MODELO_URL = ("https://storage.googleapis.com/mediapipe-models/face_landmarker/"
              "face_landmarker/float16/1/face_landmarker.task")
MODELO_PATH = os.path.join(ASSETS_DIR, 'face_landmarker.task')


def asegurar_modelo():
    if os.path.exists(MODELO_PATH):
        return True
    try:
        print("Descargando modelo de detección facial (una sola vez)...")
        urllib.request.urlretrieve(MODELO_URL, MODELO_PATH)
        return True
    except Exception as e:
        print(f"No se pudo descargar el modelo: {e}")
        print(f"Descárgalo manualmente desde:\n{MODELO_URL}\ny guárdalo en: {MODELO_PATH}")
        return False


class ControlCabeza:
    """Lee la cámara en un hilo aparte y detecta la nariz con MediaPipe FaceMesh.

    Al estar en otro hilo, el juego corre fluido a 60 FPS sin esperar a la cámara.
    """

    def __init__(self, indice_camara=0):
        # En Windows, CAP_DSHOW abre la cámara mucho más rápido que el backend por defecto
        if os.name == 'nt':
            self.cap = cv2.VideoCapture(indice_camara, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(indice_camara)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(indice_camara)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.disponible = self.cap.isOpened()
        self.landmarker = None
        self.ultimo_ts = 0

        if self.disponible:
            try:
                if not asegurar_modelo():
                    raise RuntimeError("modelo no disponible")
                opciones = vision.FaceLandmarkerOptions(
                    base_options=mp_python.BaseOptions(model_asset_path=MODELO_PATH),
                    running_mode=vision.RunningMode.VIDEO,
                    num_faces=1,
                    min_face_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                self.landmarker = vision.FaceLandmarker.create_from_options(opciones)
            except Exception as e:
                print(f"No se pudo iniciar MediaPipe: {e}")
                self.disponible = False
                self.cap.release()

        self.lock = threading.Lock()
        self.corriendo = False
        self.hilo = None

        self.nariz = None      # posición suavizada (x, y) normalizada 0..1
        self.centro = None     # posición "neutral" calibrada
        self.muestras = []
        self.frame = None      # último frame con dibujos, para mostrarlo

    def iniciar(self):
        if not self.disponible:
            return False
        self.corriendo = True
        self.hilo = threading.Thread(target=self._bucle, daemon=True)
        self.hilo.start()
        return True

    def recalibrar(self):
        with self.lock:
            self.centro = None
            self.muestras = []

    def _bucle(self):
        while self.corriendo:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue

            # Espejar para que izquierda/derecha se sientan naturales
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts = int(time.monotonic() * 1000)
            if ts <= self.ultimo_ts:  # MediaPipe exige timestamps crecientes
                ts = self.ultimo_ts + 1
            self.ultimo_ts = ts
            resultados = self.landmarker.detect_for_video(imagen, ts)

            mensaje = ""
            with self.lock:
                if resultados.face_landmarks:
                    # Landmark 1 = punta de la nariz
                    lm = resultados.face_landmarks[0][1]
                    x, y = lm.x, lm.y

                    if self.nariz is None:
                        self.nariz = (x, y)
                    else:
                        a = SUAVIZADO
                        self.nariz = (self.nariz[0] * (1 - a) + x * a,
                                      self.nariz[1] * (1 - a) + y * a)

                    # Calibración automática: promedio de las primeras muestras
                    if self.centro is None:
                        self.muestras.append(self.nariz)
                        mensaje = "Calibrando... mira al frente"
                        if len(self.muestras) >= MUESTRAS_CALIBRACION:
                            self.centro = (
                                sum(m[0] for m in self.muestras) / len(self.muestras),
                                sum(m[1] for m in self.muestras) / len(self.muestras),
                            )

                    cv2.circle(frame, (int(self.nariz[0] * w), int(self.nariz[1] * h)),
                               6, (0, 255, 0), -1)
                else:
                    self.nariz = None
                    mensaje = "No se detecta tu cara"

                # Dibuja la zona muerta alrededor del centro calibrado
                if self.centro is not None:
                    cx, cy = int(self.centro[0] * w), int(self.centro[1] * h)
                    dx, dy = int(ZONA_MUERTA_X * w), int(ZONA_MUERTA_Y * h)
                    cv2.rectangle(frame, (cx - dx, cy - dy), (cx + dx, cy + dy),
                                  (255, 255, 0), 2)

            if mensaje:
                cv2.putText(frame, mensaje, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 0, 255), 2)
            cv2.putText(frame, "C = recalibrar", (10, h - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            with self.lock:
                self.frame = frame

    @staticmethod
    def _eje(delta, zona, rango):
        if abs(delta) < zona:
            return 0.0
        signo = 1 if delta > 0 else -1
        return signo * min((abs(delta) - zona) / rango, 1.0)

    def obtener_movimiento(self):
        """Devuelve (dx, dy) entre -1 y 1. Proporcional a cuánto inclinas la cabeza."""
        with self.lock:
            nariz, centro = self.nariz, self.centro
        if nariz is None or centro is None:
            return 0.0, 0.0
        dx = self._eje(nariz[0] - centro[0], ZONA_MUERTA_X, RANGO_X)
        dy = self._eje(nariz[1] - centro[1], ZONA_MUERTA_Y, RANGO_Y)
        return dx, dy

    def mostrar_camara(self):
        """Debe llamarse desde el hilo principal (OpenCV/GUI lo requiere)."""
        with self.lock:
            frame = None if self.frame is None else self.frame.copy()
        if frame is not None:
            cv2.imshow("Camara", cv2.resize(frame, (400, 300)))
            cv2.waitKey(1)

    def cerrar(self):
        self.corriendo = False
        if self.hilo is not None:
            self.hilo.join(timeout=1)
        self.cap.release()
        if self.landmarker is not None:
            self.landmarker.close()
        cv2.destroyAllWindows()


ESTADO = {'control': None}


def precargar_camara():
    """Abre la cámara y carga el modelo en segundo plano, mientras se ve el menú."""
    def tarea():
        control = ControlCabeza(INDICE_CAMARA)
        if not control.iniciar():
            print("No se pudo abrir la cámara: se jugará solo con el teclado (WASD / flechas).")
        ESTADO['control'] = control

    threading.Thread(target=tarea, daemon=True).start()


def Manage_keys(teclas, moto, bool=True):
    if bool:
        # Control con flechas
        izq, der, arr, aba = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN
    else:
        # Control con WASD
        izq, der, arr, aba = pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s

    if teclas[izq] and moto.x > 0:
        moto.x -= moto.velocidad
    if teclas[der] and moto.x < Ancho - moto.ancho:
        moto.x += moto.velocidad
    if teclas[arr] and moto.y > 0:
        moto.y -= moto.velocidad
    if teclas[aba] and moto.y < Alto - moto.alto:
        moto.y += moto.velocidad

    limitar_moto(moto)


def limitar_moto(moto):
    moto.x = max(0, min(Ancho - moto.ancho, moto.x))
    moto.y = max(0, min(Alto - moto.alto, moto.y))
    moto.actualizar_hit_box()


def Manage_head(control, moto):
    dx, dy = control.obtener_movimiento()
    moto.x += dx * moto.velocidad
    moto.y += dy * moto.velocidad
    limitar_moto(moto)


def mostrar_menu():
    ruta_assets = ASSETS_DIR
    fondo = pygame.image.load(os.path.join(ruta_assets, 'Fondo.jpg')).convert()
    fondo = pygame.transform.scale(fondo, (Ancho, Alto))

    fondo_difuminado = fondo.copy()
    superficie_difuminado = pygame.Surface(fondo.get_size(), pygame.SRCALPHA)
    superficie_difuminado.fill((0, 0, 0, 100))
    fondo_difuminado.blit(superficie_difuminado, (0, 0))

    pygame.mixer.music.load(os.path.join(ruta_assets, 'wait.wav'))
    pygame.mixer.music.play(-1)

    font_titulo = pygame.font.Font(None, 80)
    font_opciones = pygame.font.Font(None, 50)
    font_creadores = pygame.font.Font(None, 20)

    titulo = font_titulo.render("Head Rider", True, (255, 255, 255))
    sombra_titulo = font_titulo.render("Head Rider", True, (50, 50, 50))
    texto_1jugador = font_opciones.render("1 Jugador", True, BLANCO)
    texto_2jugador = font_opciones.render("2 Jugadores", True, BLANCO)
    texto_creadores = font_creadores.render(
        "Creado por: Juan Ceballos y Angel Rodriguez", True, BLANCO)

    # Los rects se definen ANTES del bucle (antes se usaban sin existir en el primer frame)
    rect_1jugador = pygame.Rect(Ancho // 2 - 150, Alto // 2 - 50, 300, 60)
    rect_2jugador = pygame.Rect(Ancho // 2 - 150, Alto // 2 + 50, 300, 60)

    superficie_creadores = pygame.Surface((Ancho, 30), pygame.SRCALPHA)
    superficie_creadores.fill((0, 0, 0, 150))

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return None
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_1jugador.collidepoint(evento.pos):
                    return 1
                elif rect_2jugador.collidepoint(evento.pos):
                    return 2

        Ventana.blit(fondo_difuminado, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        color_1jugador = AZUL if rect_1jugador.collidepoint(mouse_pos) else (50, 50, 50)
        color_2jugador = AZUL if rect_2jugador.collidepoint(mouse_pos) else (50, 50, 50)

        pygame.draw.rect(Ventana, (30, 30, 30), rect_1jugador.move(3, 3), border_radius=10)
        pygame.draw.rect(Ventana, color_1jugador, rect_1jugador, border_radius=10)
        pygame.draw.rect(Ventana, (30, 30, 30), rect_2jugador.move(3, 3), border_radius=10)
        pygame.draw.rect(Ventana, color_2jugador, rect_2jugador, border_radius=10)

        Ventana.blit(sombra_titulo, (Ancho // 2 - sombra_titulo.get_width() // 2 + 2, 102))
        Ventana.blit(titulo, (Ancho // 2 - titulo.get_width() // 2, 100))

        Ventana.blit(texto_1jugador, (Ancho // 2 - texto_1jugador.get_width() // 2, Alto // 2 - 35))
        Ventana.blit(texto_2jugador, (Ancho // 2 - texto_2jugador.get_width() // 2, Alto // 2 + 65))

        Ventana.blit(superficie_creadores, (0, Alto - 30))
        Ventana.blit(texto_creadores, (Ancho // 2 - texto_creadores.get_width() // 2, Alto - 25))

        pygame.display.update()
        RELOJ.tick(FPS)


def mostrar_ganador(jugador, Ancho, Alto, Ventana, BLANCO, AZUL, NEGRO, numero_de_jugadores, puntaje):
    """Pantalla final. Devuelve True para volver al menú, False si se cierra la ventana."""
    ruta_assets = ASSETS_DIR
    pygame.mixer.music.load(os.path.join(ruta_assets, 'dead.wav'))
    pygame.mixer.music.play()

    for i in range(Alto):
        r = int(max(0, 30 - i * 0.05))
        g = int(max(0, 20 - i * 0.03))
        b = int(max(0, 50 - i * 0.07))
        pygame.draw.line(Ventana, (r, g, b), (0, i), (Ancho, i))

    font_titulo = pygame.font.Font(None, 70)
    font_subtitulo = pygame.font.Font(None, 50)
    font_boton = pygame.font.Font(None, 40)

    if numero_de_jugadores != 1:
        texto_ganador_linea1 = font_titulo.render("Jugador", True, BLANCO)
        texto_ganador_linea2 = font_titulo.render(f"{jugador} ha ganado", True, BLANCO)
    else:
        texto_ganador_linea1 = font_titulo.render("Juego", True, BLANCO)
        texto_ganador_linea2 = font_titulo.render("Terminado", True, BLANCO)
    rect_ganador_linea1 = texto_ganador_linea1.get_rect(center=(Ancho // 2, Alto // 2 - 130))
    rect_ganador_linea2 = texto_ganador_linea2.get_rect(center=(Ancho // 2, Alto // 2 - 70))

    texto_puntaje = font_subtitulo.render(f"Puntaje: {puntaje}", True, (200, 200, 200))
    texto_volver_a_jugar = font_boton.render("Volver a jugar", True, BLANCO)

    rect_puntaje = texto_puntaje.get_rect(center=(Ancho // 2, Alto // 2 - 20))
    rect_volver_a_jugar = pygame.Rect(0, 0, 300, 60)
    rect_volver_a_jugar.center = (Ancho // 2, Alto // 2 + 100)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        Ventana.blit(texto_ganador_linea1, rect_ganador_linea1)
        Ventana.blit(texto_ganador_linea2, rect_ganador_linea2)
        Ventana.blit(texto_puntaje, rect_puntaje)

        color_boton = AZUL if rect_volver_a_jugar.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(Ventana, (20, 20, 20), rect_volver_a_jugar.move(3, 3), border_radius=10)
        pygame.draw.rect(Ventana, color_boton, rect_volver_a_jugar, border_radius=10)
        Ventana.blit(texto_volver_a_jugar,
                     texto_volver_a_jugar.get_rect(center=rect_volver_a_jugar.center))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_volver_a_jugar.collidepoint(evento.pos):
                    pygame.mixer.music.stop()
                    return True  # main() vuelve a mostrar el menú (antes salía el menú dos veces)

        pygame.display.update()
        RELOJ.tick(FPS)


def detectar_colision(carros, motos):
    for carro in carros:
        for moto in motos:
            if carro.rect.colliderect(moto.rect):
                return True
    return False


def iniciar_juego(num_jugadores):
    """Devuelve True para volver al menú, False para cerrar el programa."""
    ruta_assets = ASSETS_DIR
    pygame.mixer.music.load(os.path.join(ruta_assets, 'tokyo_drift.wav'))
    pygame.mixer.music.play(-1)

    Jugadores = []
    Enemigos = []

    escenario = Escenario(Ancho, Alto)
    generador_carros = Generador(Ancho, escenario.carriles)

    tiempo_inicio = pygame.time.get_ticks()
    font = pygame.font.Font(None, 36)

    moto_1 = Moto(100, 400, ruta_assets, 'blue')
    Jugadores.append(moto_1)

    if num_jugadores == 2:
        moto_2 = Moto(275, 400, ruta_assets, 'red')
        Jugadores.append(moto_2)

    # Temporizador de cambio de escenario
    tiempo_ultimo_cambio = pygame.time.get_ticks()
    tiempo_entre_cambios = 10000

    # La cámara ya se está cargando (o cargó) en segundo plano desde que abrió el programa
    control = ESTADO['control']
    if control is not None:
        control.recalibrar()

    try:
        while True:
            if control is None and ESTADO['control'] is not None:
                control = ESTADO['control']  # terminó de cargar durante la partida
                control.recalibrar()

            tiempo_actual = pygame.time.get_ticks()
            Enemigos = generador_carros.actualizar(Enemigos)

            tiempo_transcurrido = (tiempo_actual - tiempo_inicio) // 1000
            texto_tiempo = font.render(f"Puntaje: {tiempo_transcurrido:03d}", True, BLANCO)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    return False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        escenario.cambiar_tema(random.choice(list(escenario.temas.keys())))
                    elif evento.key == pygame.K_c and control is not None:
                        control.recalibrar()

            teclas = pygame.key.get_pressed()

            # Jugador 1: cabeza (+ WASD como respaldo)
            Manage_keys(teclas, moto_1, False)
            if control is not None and control.disponible:
                Manage_head(control, moto_1)

            # Jugador 2: flechas
            if num_jugadores == 2:
                Manage_keys(teclas, moto_2)

            # Cambiar escenario automáticamente
            if tiempo_actual - tiempo_ultimo_cambio > tiempo_entre_cambios:
                escenario.cambiar_tema(random.choice(list(escenario.temas.keys())))
                tiempo_ultimo_cambio = tiempo_actual

            escenario.actualizar()
            escenario.dibujar(Ventana)
            Ventana.blit(texto_tiempo, (10, 10))

            moto_1.dibujar(Ventana)
            if num_jugadores == 2:
                moto_2.dibujar(Ventana)

            if tiempo_transcurrido < 10:
                aumento = 2
            else:
                aumento = min((tiempo_transcurrido // 10) + 3, 7)

            # Se recorre una copia para poder quitar carros sin romper el bucle
            for enemigo in Enemigos[:]:
                enemigo.dibujar(Ventana)
                enemigo.movimiento(aumento)

                if detectar_colision([enemigo], [moto_1]):
                    pygame.mixer.music.stop()
                    return mostrar_ganador(2, Ancho, Alto, Ventana, BLANCO, AZUL, NEGRO,
                                           num_jugadores, tiempo_transcurrido)

                if num_jugadores == 2 and detectar_colision([enemigo], [moto_2]):
                    pygame.mixer.music.stop()
                    return mostrar_ganador(1, Ancho, Alto, Ventana, BLANCO, AZUL, NEGRO,
                                           num_jugadores, tiempo_transcurrido)

                if enemigo.y > Alto:
                    Enemigos.remove(enemigo)

            pygame.display.update()

            # Vista previa de la cámara (dentro del bucle y en el hilo principal)
            if control is not None and control.disponible:
                control.mostrar_camara()

            RELOJ.tick(FPS)
    finally:
        # Solo se cierra la ventana de vista previa; la cámara sigue lista para la próxima partida
        cv2.destroyAllWindows()


def main():
    precargar_camara()  # se carga mientras estás en el menú
    while True:
        num_jugadores = mostrar_menu()
        if num_jugadores is None:
            break
        if not iniciar_juego(num_jugadores):
            break

    if ESTADO['control'] is not None:
        ESTADO['control'].cerrar()
    pygame.quit()


if __name__ == "__main__":
    main()
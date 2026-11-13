import pygame
import random
from motos import Moto
from carros import Carro, Generador
from escenarios import Escenario
import os

# Rutas relativas: carpeta `assets` junto al archivo `trafic_raider.py`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
# Inicialización de Pygame y configuración de la ventana
pygame.init()
Ancho = 400
Alto = 600
Ventana = pygame.display.set_mode((Ancho, Alto))
pygame.display.set_caption("Traffic Rider")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)

def Manage_keys(teclas, moto, bool = True):
    if bool:
        # Control con flechas
        if teclas[pygame.K_LEFT]:
            if moto.x > 0:
                moto.x -= moto.velocidad
                moto.actualizar_hit_box()
        if teclas[pygame.K_RIGHT]:
            if moto.x < Ancho - moto.ancho:
                moto.x += moto.velocidad
                moto.actualizar_hit_box()
        if teclas[pygame.K_UP]:
            if moto.y > 0:
                moto.y -= moto.velocidad
                moto.actualizar_hit_box()
        if teclas[pygame.K_DOWN]:
            if moto.y < Alto - moto.alto:
                moto.y += moto.velocidad
                moto.actualizar_hit_box()
    else:
        # Control con WASD
        if teclas[pygame.K_a]:
            if moto.x > 0:
                moto.x -= moto.velocidad
                moto.actualizar_hit_box()
                
        if teclas[pygame.K_d]:
            if moto.x < Ancho - moto.ancho:
                moto.x += moto.velocidad
                moto.actualizar_hit_box()
        if teclas[pygame.K_w]:
            if moto.y > 0:
                moto.y -= moto.velocidad
                moto.actualizar_hit_box()
        if teclas[pygame.K_s]:
            if moto.y < Alto - moto.alto:
                moto.y += moto.velocidad
                moto.actualizar_hit_box()
def mostrar_menu():
    ruta_assets = ASSETS_DIR
    fondo = pygame.image.load(os.path.join(ruta_assets, 'Fondo.png'))
    fondo = pygame.transform.scale(fondo, (Ancho, Alto))  # Ajustar al tamaño de la ventana
    
    # Aplicar un efecto de difuminado al fondo
    fondo_difuminado = fondo.copy()
    superficie_difuminado = pygame.Surface(fondo.get_size(), pygame.SRCALPHA)
    superficie_difuminado.fill((0, 0, 0, 100))  # Capa semitransparente
    fondo_difuminado.blit(superficie_difuminado, (0, 0))
    
    # Cargar música
    pygame.mixer.music.load(os.path.join(ruta_assets, 'wait.wav'))
    pygame.mixer.music.play(-1)  # Reproducir en bucle
    
    menu_activo = True
    seleccion = None
    
    # Configuración del texto
    font_titulo = pygame.font.Font(None, 80)  # Título más grande
    font_opciones = pygame.font.Font(None, 50)
    
    titulo = font_titulo.render("Traffic Rider", True, (255, 255, 255))
    texto_1jugador = font_opciones.render("1 Jugador", True, BLANCO)
    texto_2jugador = font_opciones.render("2 Jugadores", True, BLANCO)
    
    while menu_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return None
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if rect_1jugador.collidepoint(mouse_pos):
                    return 1
                elif rect_2jugador.collidepoint(mouse_pos):
                    return 2
        
        # Dibujar fondo difuminado
        Ventana.blit(fondo_difuminado, (0, 0))
        
        # Obtener posición del mouse
        mouse_pos = pygame.mouse.get_pos()
        
        # Crear rectángulos para los botones
        rect_1jugador = pygame.Rect(Ancho//2 - 150, Alto//2 - 50, 300, 60)
        rect_2jugador = pygame.Rect(Ancho//2 - 150, Alto//2 + 50, 300, 60)
        
        # Dibujar los botones con efecto de hover
        color_1jugador = AZUL if rect_1jugador.collidepoint(mouse_pos) else (50, 50, 50)
        color_2jugador = AZUL if rect_2jugador.collidepoint(mouse_pos) else (50, 50, 50)
        
        # Dibujar rectángulos con sombra y efecto de profundidad
        pygame.draw.rect(Ventana, (30, 30, 30), rect_1jugador.move(3, 3), border_radius=10)  # Sombra
        pygame.draw.rect(Ventana, color_1jugador, rect_1jugador, border_radius=10)
        
        pygame.draw.rect(Ventana, (30, 30, 30), rect_2jugador.move(3, 3), border_radius=10)  # Sombra
        pygame.draw.rect(Ventana, color_2jugador, rect_2jugador, border_radius=10)
        
        # Posicionar los textos
        # Título con efecto de contorno
        sombra_titulo = font_titulo.render("Traffic Rider", True, (50, 50, 50))
        Ventana.blit(sombra_titulo, (Ancho//2 - sombra_titulo.get_width()//2 + 2, 102))
        Ventana.blit(titulo, (Ancho//2 - titulo.get_width()//2, 100))
        
        # Texto de los botones centrado
        Ventana.blit(texto_1jugador, (Ancho//2 - texto_1jugador.get_width()//2, Alto//2 - 35))
        Ventana.blit(texto_2jugador, (Ancho//2 - texto_2jugador.get_width()//2, Alto//2 + 65))
        
        # Rectángulo de creadores con efecto de transparencia
        rect_creadores = pygame.Rect(0, Alto - 30, Ancho, 30)
        superficie_creadores = pygame.Surface((Ancho, 30), pygame.SRCALPHA)
        superficie_creadores.fill((0, 0, 0, 150))  # Fondo semi-transparente
        Ventana.blit(superficie_creadores, (0, Alto - 30))
        
        # Texto de creadores
        font_creadores = pygame.font.Font(None, 20)
        texto_creadores = font_creadores.render("Creado por: Juan Ceballos y Angel Rodriguez", True, BLANCO)
        Ventana.blit(texto_creadores, (Ancho // 2 - texto_creadores.get_width() // 2, Alto - 25))
        
        # Actualizar pantalla
        pygame.display.update()
    
    return seleccion


def mostrar_ganador(jugador, Ancho, Alto, Ventana, BLANCO, AZUL, NEGRO, numero_de_jugadores, puntaje):
    ruta_assets = ASSETS_DIR
    # Cargar y reproducir música de fondo
    pygame.mixer.music.load(os.path.join(ruta_assets, 'dead.wav'))
    pygame.mixer.music.play()  # Reproducir solo una vez
    
    # Crear un fondo degradado
    for i in range(Alto):
        # Crear un degradado de color que vaya de un tono oscuro a otro
        r = int(max(0, 30 - i * 0.05))
        g = int(max(0, 20 - i * 0.03))
        b = int(max(0, 50 - i * 0.07))
        pygame.draw.line(Ventana, (r, g, b), (0, i), (Ancho, i))
    
    # Configuración de fuentes
    font_titulo = pygame.font.Font(None, 70)
    font_subtitulo = pygame.font.Font(None, 50)
    font_boton = pygame.font.Font(None, 40)
    
    # Preparar textos
    if numero_de_jugadores != 1:
        # Dividir "Jugador X ha ganado" en dos líneas
        texto_ganador_linea1 = font_titulo.render("Jugador", True, BLANCO)
        texto_ganador_linea2 = font_titulo.render(f"{jugador} ha ganado", True, BLANCO)
        rect_ganador_linea1 = texto_ganador_linea1.get_rect(center=(Ancho // 2, Alto // 2 - 130))
        rect_ganador_linea2 = texto_ganador_linea2.get_rect(center=(Ancho // 2, Alto // 2 - 70))
    else:
        # Dividir "Juego Terminado" en dos líneas
        texto_ganador_linea1 = font_titulo.render("Juego", True, BLANCO)
        texto_ganador_linea2 = font_titulo.render("Terminado", True, BLANCO)
        rect_ganador_linea1 = texto_ganador_linea1.get_rect(center=(Ancho // 2, Alto // 2 - 130))
        rect_ganador_linea2 = texto_ganador_linea2.get_rect(center=(Ancho // 2, Alto // 2 - 70))
    
    texto_puntaje = font_subtitulo.render(f"Puntaje: {puntaje}", True, (200, 200, 200))
    texto_volver_a_jugar = font_boton.render("Volver a jugar", True, BLANCO)
    
    # Crear rectángulos para posicionamiento
    rect_puntaje = texto_puntaje.get_rect(center=(Ancho // 2, Alto // 2 - 20))
    
    # Crear rectángulo para el botón con un área más grande
    rect_volver_a_jugar = pygame.Rect(0, 0, 300, 60)
    rect_volver_a_jugar.center = (Ancho // 2, Alto // 2 + 100)
    
    # Bucle principal de la pantalla de ganador
    volver_a_jugar = False
    while not volver_a_jugar:
        # Obtener posición del mouse
        mouse_pos = pygame.mouse.get_pos()
        
        # Dibujar título y puntaje
        # Dibujar las dos líneas del título
        Ventana.blit(texto_ganador_linea1, rect_ganador_linea1)
        Ventana.blit(texto_ganador_linea2, rect_ganador_linea2)
        
        Ventana.blit(texto_puntaje, rect_puntaje)
        
        # Efecto de hover para el botón
        color_boton = AZUL if rect_volver_a_jugar.collidepoint(mouse_pos) else (50, 50, 50)
        
        # Dibujar sombra del botón
        pygame.draw.rect(Ventana, (20, 20, 20), rect_volver_a_jugar.move(3, 3), border_radius=10)
        
        # Dibujar botón
        pygame.draw.rect(Ventana, color_boton, rect_volver_a_jugar, border_radius=10)
        
        # Dibujar texto del botón
        rect_texto_boton = texto_volver_a_jugar.get_rect(center=rect_volver_a_jugar.center)
        Ventana.blit(texto_volver_a_jugar, rect_texto_boton)
        
        # Manejar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return None
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_volver_a_jugar.collidepoint(evento.pos):
                    volver_a_jugar = True
                    pygame.mixer.music.stop()
                    return mostrar_menu()
        
        # Actualizar pantalla
        pygame.display.update()

    return None
    
def detectar_colision(carros, motos):
    for carro in carros:
        for moto in motos:
            if carro.rect.colliderect(moto.rect):
                
                return True
    return False


def iniciar_juego(num_jugadores):
    ruta_assets = ASSETS_DIR
    # Cargar y reproducir música de fondo
    pygame.mixer.music.load(os.path.join(ruta_assets, 'tokyo_drift.wav'))
    pygame.mixer.music.play(-1)  # Reproducir en bucle
    jugando = True
    Jugadores = []
    Enemigos = []
    
    
    
    # Crear escenario
    escenario = Escenario(Ancho, Alto)
    
    generador_carros = Generador(Ancho, escenario.carriles)

    # Configuración del temporizador
    tiempo_inicio = pygame.time.get_ticks()
    font = pygame.font.Font(None, 36)  # Fuente para el contador
    
    # Crear jugadores según la selección
    moto_1 = Moto(100, 400 , ruta_assets , 'blue')
    Jugadores.append(moto_1)
    
    if num_jugadores == 2:
        moto_2 = Moto(275, 400, ruta_assets, 'red')
        Jugadores.append(moto_2)
    
    # Variable para controlar el cambio de escenario
    tiempo_ultimo_cambio = pygame.time.get_ticks()
    tiempo_entre_cambios = 10000  # 5 segundos
    
    while jugando:
        tiempo_actual = pygame.time.get_ticks()
        
        Enemigos = generador_carros.actualizar(Enemigos)

        # Calcular tiempo transcurrido en segundos
        tiempo_transcurrido = (tiempo_actual - tiempo_inicio) // 1000
        
        # Crear texto del temporizador
        texto_tiempo = font.render(f"Puntaje: {tiempo_transcurrido:03d}", True, BLANCO)
        
        eventos = pygame.event.get()
        teclas = pygame.key.get_pressed()
        
        # Gestionar teclas para cada jugador
        Manage_keys(teclas, moto_1, False)
        if num_jugadores == 2:
            Manage_keys(teclas, moto_2)
        
        # Cambiar escenario automáticamente cada 10 segundos
        if tiempo_actual - tiempo_ultimo_cambio > tiempo_entre_cambios:
            temas = list(escenario.temas.keys())
            nuevo_tema = random.choice(temas)
            escenario.cambiar_tema(nuevo_tema)
            tiempo_ultimo_cambio = tiempo_actual
        
        # Actualizar y dibujar escenario
        escenario.actualizar()
        escenario.dibujar(Ventana)
        
        # Dibujar el temporizador en la parte superior
        Ventana.blit(texto_tiempo, (10, 10))
        
        # Dibujar jugadores
        moto_1.dibujar(Ventana)
        if num_jugadores == 2:
            moto_2.dibujar(Ventana)
            
        # Dibujar enemigos
        for enemigo in Enemigos:
            enemigo.dibujar(Ventana)
            if tiempo_transcurrido < 10:
                enemigo.movimiento(2)    
                
            else:
                enemigo.movimiento((tiempo_transcurrido // 10)+ 3)
                
            if detectar_colision([enemigo], [moto_1]):
                pygame.mixer.music.stop()
                mostrar_ganador(2, Ancho, Alto, Ventana, BLANCO, AZUL, NEGRO, num_jugadores, tiempo_transcurrido)
                return
            
            if num_jugadores == 2 and detectar_colision([enemigo], [moto_2]):
                pygame.mixer.music.stop()
                mostrar_ganador(1, Ancho, Alto, Ventana, BLANCO, AZUL, NEGRO, num_jugadores, tiempo_transcurrido)
                return
            
            # Eliminar carros cuando se salgan de el limite inferior de la pantalla
            if enemigo.y > Alto:
                Enemigos.remove(enemigo)
            
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.mixer.music.stop()
                jugando = False
            # Cambiar escenario manualmente con la tecla ESPACIO
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    temas = list(escenario.temas.keys())
                    nuevo_tema = random.choice(temas)
                    escenario.cambiar_tema(nuevo_tema)
    
        pygame.display.update()
        
        
def main():
    while True:
        num_jugadores = mostrar_menu()
        if num_jugadores is None:
            break
        iniciar_juego(num_jugadores)
    
    pygame.quit()

if __name__ == "__main__":
    main()
import pygame 
import random
import os

# Rutas relativas: carpeta `assets` junto al archivo `carros.py`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
class Carro:

    def __init__(self, posicion, color):
        self.stilos = ['car_black_1.png', 'car_blue_1.png', 'car_green_2.png', 'car_red_1.png', 'car_yellow_1.png',
                       'car_black_2.png', 'car_blue_2.png', 'car_green_1.png', 'car_red_2.png', 'car_yellow_2.png',
                       'car_black_3.png', 'car_blue_3.png', 'car_green_3.png', 'car_red_3.png', 'car_yellow_3.png',
                       'car_black_4.png', 'car_blue_4.png', 'car_green_4.png', 'car_red_4.png', 'car_yellow_4.png',
                       'car_black_5.png', 'car_blue_5.png', 'car_green_5.png', 'car_red_5.png', 'car_yellow_5.png']
        self.x = posicion[0]
        self.y = posicion[1]
        self.ancho = 75
        self.alto = 100
        self.velocidad = 0.1
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto) 
        # Usar la carpeta `assets` relativa a este archivo
        self.ruta_assets = ASSETS_DIR
        
        try:
            self.imagen = pygame.image.load(os.path.join(self.ruta_assets, random.choice(self.stilos)))
            self.imagen = pygame.transform.scale(self.imagen, (self.ancho, self.alto))
            self.imagen = pygame.transform.rotate(self.imagen, 180)
        except pygame.error as e:
            print(f"No se pudo cargar la imagen: {e}")
            # Crear un rectángulo de color como respaldo
            self.imagen = pygame.Surface((self.ancho, self.alto))
            self.imagen.fill(self.color)
        
    def dibujar(self, ventana):
        ventana.blit(self.imagen, (self.x, self.y))
        
    def movimiento(self, aumento):
        self.y += self.velocidad * aumento
        self.rect.topleft = (self.x, self.y)
        
    def aumentar_velocidad(self):
        self.velocidad += 0.01
        
class Generador:
    def __init__(self, ancho_ventana, carriles):
        self.ancho_ventana = ancho_ventana
        self.carriles = carriles
        self.tiempo_ultimo_carro = pygame.time.get_ticks()
        self.intervalo_inicial = 2000  # 3 segundos entre carros al inicio
        self.intervalo_minimo = 800    # Mínimo tiempo entre carros
        self.tiempo_inicio = pygame.time.get_ticks()
        
    def tiempo_espera(self):
        # Reduce el intervalo cada 10 segundos
        tiempo_transcurrido = (pygame.time.get_ticks() - self.tiempo_inicio) // 1000
        reduccion = (tiempo_transcurrido // 10) * 400  # Reduce 200ms cada 10 segundos
        nuevo_intervalo = max(self.intervalo_inicial - reduccion, self.intervalo_minimo)
        return nuevo_intervalo
        
    def actualizar(self, carros):
        tiempo_actual = pygame.time.get_ticks()
        intervalo_actual = self.tiempo_espera()
        
        # Verificar si es tiempo de generar un nuevo carro
        if tiempo_actual - self.tiempo_ultimo_carro > intervalo_actual:
            # Seleccionar un carril aleatorio
            carril_x = random.choice(self.carriles)
            
            # Ajustar la posición para centrar el carro en el carril
            pos_x = carril_x - 37.5  # La mitad del ancho del carro (75/2)
            
            # Crear nuevo carro
            nuevo_carro = Carro((pos_x, -100), (255, 0, 0))  # Empieza arriba de la pantalla
            
            # Aumentar velocidad según el tiempo transcurrido
            tiempo_transcurrido = (tiempo_actual - self.tiempo_inicio) // 1000
            velocidad_adicional = min(tiempo_transcurrido // 15 * 0.05, 0.3)  # Aumenta cada 15 segundos
            nuevo_carro.velocidad += velocidad_adicional
            
            carros.append(nuevo_carro)
            self.tiempo_ultimo_carro = tiempo_actual
        
        # Limpiar carros que están fuera de la pantalla
        return [carro for carro in carros if carro.y < 700]
        
        
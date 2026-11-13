import pygame 
import os

# Rutas relativas: carpeta `assets` junto al archivo `motos.py`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

class Moto:

    def __init__(self, x, y, ruta_imagen,color):
        self.x = x
        self.y = y
        self.ancho = 50
        self.alto = 100
        self.velocidad = 0.2
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto) 
        try:
            # Si se pasó una ruta válida, usarla; si no, usar la carpeta assets del módulo
            if ruta_imagen and os.path.isdir(ruta_imagen):
                image_path = os.path.join(ruta_imagen, f'motorcycle_{color}.png')
            else:
                image_path = os.path.join(ASSETS_DIR, f'motorcycle_{color}.png')
            self.imagen = pygame.image.load(image_path)
            self.imagen = pygame.transform.scale(self.imagen, (self.ancho, self.alto))
        except pygame.error as e:
            print(f"No se pudo cargar la imagen: {e}")
            # Crear un rectángulo de color como respaldo
            self.imagen = pygame.Surface((self.ancho, self.alto))
            self.imagen.fill((150, 150, 150))
            
    def dibujar(self, ventana):
        ventana.blit(self.imagen, (self.x, self.y))
        
    def actualizar_hit_box(self):
        self.rect.topleft = (self.x, self.y)
        
    
        
        
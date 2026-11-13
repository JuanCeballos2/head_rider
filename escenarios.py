import pygame

class Escenario:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.carril_ancho = ancho // 3  # Divide la pantalla en 3 carriles
        # Posiciones X de los carriles (centro de cada carril)
        self.carriles = [
            self.carril_ancho // 2,           # Carril izquierdo
            self.carril_ancho + self.carril_ancho // 2,  # Carril central
            2 * self.carril_ancho + self.carril_ancho // 2   # Carril derecho
        ]
        
        # Definir diferentes temas de escenarios
        self.temas = {
            "clasico": {
                "fondo": (50, 50, 50),  # Gris oscuro
                "lineas": (255, 255, 255),  # Blanco
                "bordes": (255, 255, 0)  # Amarillo
            },
            "noche": {
                "fondo": (20, 20, 30),  # Azul muy oscuro
                "lineas": (0, 255, 255),  # Cyan
                "bordes": (255, 140, 0)  # Naranja
            },
            "desierto": {
                "fondo": (194, 178, 128),  # Arena
                "lineas": (139, 69, 19),  # Marrón
                "bordes": (255, 140, 0)  # Naranja
            }
        }
        self.tema_actual = "clasico"
        
        # Variables para la animación de las líneas
        self.lineas_y = [i for i in range(0, alto, 80)]  # Posiciones Y de las líneas
        self.velocidad_lineas = 0.1  # Velocidad reducida para movimiento más suave
        
    def cambiar_tema(self, tema):
        if tema in self.temas:
            self.tema_actual = tema
            
    def actualizar(self):
        # Actualizar posición de las líneas
        for i in range(len(self.lineas_y)):
            self.lineas_y[i] += self.velocidad_lineas
            if self.lineas_y[i] > self.alto:
                self.lineas_y[i] = -40
                
    def dibujar(self, ventana):
        # Dibujar fondo
        ventana.fill(self.temas[self.tema_actual]["fondo"])
        
        # Dibujar líneas de los carriles
        for y in self.lineas_y:
            # Líneas discontinuas entre carriles
            pygame.draw.rect(ventana, self.temas[self.tema_actual]["lineas"],
                           (self.carril_ancho - 5, y, 10, 40))
            pygame.draw.rect(ventana, self.temas[self.tema_actual]["lineas"],
                           (2 * self.carril_ancho - 5, y, 10, 40))
        
        # Dibujar bordes de la carretera
        pygame.draw.rect(ventana, self.temas[self.tema_actual]["bordes"],
                        (0, 0, 10, self.alto))  # Borde izquierdo
        pygame.draw.rect(ventana, self.temas[self.tema_actual]["bordes"],
                        (self.ancho - 10, 0, 10, self.alto))  # Borde derecho

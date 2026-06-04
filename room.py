import pygame

ANCHO = 800
ALTO = 600

COLOR_FONDO = (30, 10, 40)      # morado oscuro
COLOR_PISO = (80, 40, 90)       # morado medio
COLOR_PARED = (200, 80, 20)     # naranja

def dibujar(pantalla):
    pantalla.fill(COLOR_FONDO)
    pygame.draw.rect(pantalla, COLOR_PISO, (0, ALTO - 120, ANCHO, 120))
    pygame.draw.rect(pantalla, COLOR_PARED, (0, 0, ANCHO, 10))
    pygame.draw.rect(pantalla, COLOR_PARED, (0, 0, 10, ALTO))
    pygame.draw.rect(pantalla, COLOR_PARED, (ANCHO - 10, 0, 10, ALTO))

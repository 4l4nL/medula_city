import pygame
from room import ANCHO, ALTO, dibujar as dibujar_sala
from player import Player

FPS = 60

class Game:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Medula City")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.jugador = Player()

    def run(self):
        while self.corriendo:
            self._eventos()
            self._actualizar()
            self._dibujar()
            self.reloj.tick(FPS)

    def _eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.corriendo = False

    def _actualizar(self):
        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas)

    def _dibujar(self):
        dibujar_sala(self.pantalla)
        self.jugador.dibujar(self.pantalla)
        pygame.display.flip()

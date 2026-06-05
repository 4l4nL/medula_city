import pygame

VELOCIDAD = 4
COLOR = (255, 255, 255)

class Player:
    """Representa al jugador controlado por el usuario."""

    def __init__(self):
        self.x = 400
        self.y = 300
        self.ancho = 32
        self.alto = 48
        self.frame = 0
        self.tiempo_frame = 0
        self.moviendose = False

    def mover(self, teclas):
        """Mover el jugador según las teclas pulsadas."""
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.x -= VELOCIDAD
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.x += VELOCIDAD
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.y -= VELOCIDAD
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.y += VELOCIDAD

        # colisiones: impide salir de los límites de la sala
        self.x = max(10, min(self.x, 800 - self.ancho - 10))
        self.y = max(10, min(self.y, 600 - self.alto - 10))

        # detecta si alguna tecla de movimiento está presionada
        self.moviendose = (
            teclas[pygame.K_LEFT] or teclas[pygame.K_a] or
            teclas[pygame.K_RIGHT] or teclas[pygame.K_d] or
            teclas[pygame.K_UP] or teclas[pygame.K_w] or
            teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        )

        # avanza el frame de animación cada 10 ciclos del juego
        if self.moviendose:
            self.tiempo_frame += 1
            if self.tiempo_frame >= 10:
                self.tiempo_frame = 0
                self.frame = (self.frame + 1) % 4
        else:
            self.frame = 0

    def dibujar(self, pantalla):
        """Dibujar el jugador en la pantalla."""
        x, y = self.x, self.y
        w, h = self.ancho, self.alto

        # cabeza
        pygame.draw.ellipse(pantalla, COLOR, (x, y, w, w))
        # ojos
        pygame.draw.circle(pantalla, (0, 0, 0), (x + 9, y + 11), 5)
        pygame.draw.circle(pantalla, (0, 0, 0), (x + 23, y + 11), 5)
        # nariz
        pygame.draw.polygon(pantalla, (0, 0, 0), [
            (x + 16, y + 16), (x + 13, y + 22), (x + 19, y + 22)
        ])
        # sonrisa
        pygame.draw.arc(pantalla, (0, 0, 0),
                        (x + 8, y + 20, 16, 8), 3.14, 0, 2)
        # cuerpo
        pygame.draw.rect(pantalla, COLOR, (x + 6, y + w, w - 12, h - w - 8))

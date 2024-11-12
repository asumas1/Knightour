import pygame
import sys

# Iniciar pygame
pygame.init()

# Definir el tamaño de la ventana
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colores
WHITE = (255, 255, 255)  # Casillas claras
RED = (120, 9, 1)  # Casillas oscuras rojas
GRAY = (128, 128, 128)  # Color del grafo
BLACK = (0, 0, 0)

# Definir el delay
DELAY = 200

# Crear la ventana
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("cavallo simulator")

# Cargar la imagen del caballo
knight_img = pygame.image.load("caballo.png")
knight_img = pygame.transform.scale(knight_img, (SQUARE_SIZE, SQUARE_SIZE))

# Movimientos posibles del caballo
knight_moves = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

# Función para convertir coordenadas numéricas a notación algebraica
def to_algebraic(x, y):
    columns = "abcdefgh"
    return f"{columns[y]}{8 - x}"

# Clase para manejar el recorrido del caballo
class KnightTour:
    def __init__(self, start_x, start_y):
        self.board = [[-1 for _ in range(COLS)] for _ in range(ROWS)]
        self.path = []
        self.move_index = 0
        self.last_move_time = pygame.time.get_ticks()

        # Inicializar con la posición de inicio
        self.start_x = start_x
        self.start_y = start_y
        self.board[start_x][start_y] = 0
        self.path.append((start_x, start_y))

        # Imprimir el movimiento inicial
        print(f"Movimiento 0: {to_algebraic(start_x, start_y)}")

    def is_valid(self, x, y):
        return 0 <= x < ROWS and 0 <= y < COLS and self.board[x][y] == -1

    def get_next_move(self, curr_x, curr_y):
        move_options = []
        for move in knight_moves:
            next_x, next_y = curr_x + move[0], curr_y + move[1]
            if self.is_valid(next_x, next_y):
                count = 0
                for next_move in knight_moves:
                    next_next_x, next_next_y = next_x + next_move[0], next_y + next_move[1]
                    if self.is_valid(next_next_x, next_next_y):
                        count += 1
                move_options.append((count, next_x, next_y))

        move_options.sort()
        return move_options

    def advance_tour(self):
        if self.move_index >= len(self.path):
            return False

        curr_x, curr_y = self.path[-1]
        move_count = len(self.path)

        next_moves = self.get_next_move(curr_x, curr_y)
        for _, next_x, next_y in next_moves:
            self.board[next_x][next_y] = move_count
            self.path.append((next_x, next_y))
            print(f"Movimiento {move_count}: {to_algebraic(next_x, next_y)}")
            return True

        # Si no hay movimientos válidos, finaliza el recorrido
        return False

# Clase para manejar el juego
class Game:
    def __init__(self):
        self.tour = None  # Inicia sin recorrido
        self.delay = DELAY
        self.selecting_start = True  # Para permitir seleccionar casilla inicial
        self.simulation_completed = False  # Verifica si la simulación terminó
        self.ready_to_clear = False  # Estado para borrar el grafo y el caballo tras un clic

    @staticmethod
    def draw_board(path):
        win.fill(WHITE)
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    pygame.draw.rect(win, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        if len(path) > 1:
            for i in range(1, len(path)):
                start_pos = (path[i-1][1] * SQUARE_SIZE + SQUARE_SIZE // 2, path[i-1][0] * SQUARE_SIZE + SQUARE_SIZE // 2)
                end_pos = (path[i][1] * SQUARE_SIZE + SQUARE_SIZE // 2, path[i][0] * SQUARE_SIZE + SQUARE_SIZE // 2)
                pygame.draw.line(win, GRAY, start_pos, end_pos, 5)

        for i, (row, col) in enumerate(path):
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(win, GRAY, (center_x, center_y), 10)

            if i == len(path) - 1:
                win.blit(knight_img, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        pygame.display.update()

    def draw_empty_board(self):
        """Dibuja el tablero vacío, sin el grafo ni el caballo"""
        win.fill(WHITE)
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    pygame.draw.rect(win, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.update()

    def handle_click(self, pos):
        col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
        if self.selecting_start and not self.simulation_completed:
            # Establecer la posición inicial del caballo
            self.tour = KnightTour(row, col)
            self.selecting_start = False
        elif self.simulation_completed and self.ready_to_clear:
            # Borrar el grafo y reiniciar el tablero cuando se haga clic después de la simulación
            self.simulation_completed = False
            self.ready_to_clear = False
            self.tour = None
            self.selecting_start = True
            self.draw_empty_board()  # Tablero vacío

    def run(self):
        running = True
        self.draw_empty_board()  # Dibuja el tablero vacío al inicio
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            if self.tour and not self.selecting_start:
                current_time = pygame.time.get_ticks()
                if current_time - self.tour.last_move_time > self.delay:
                    self.tour.last_move_time = current_time
                    if not self.tour.advance_tour():
                        print("Tour completado. Haz clic para borrar el grafo.")
                        self.simulation_completed = True
                        self.ready_to_clear = True

                self.draw_board(self.tour.path)

        pygame.quit()
        sys.exit()

# Ejecutar el juego
if __name__ == "__main__":
    game = Game()
    game.run()

#cyka blyat

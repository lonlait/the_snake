import random
import sys

import pygame

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Центр экрана

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Colors
BACKGROUND_COLOR = (0, 0, 0)
BOARD_BACKGROUND_COLOR = BACKGROUND_COLOR
SNAKE_COLOR = (0, 255, 0)
APPLE_COLOR = (255, 0, 0)
BORDER_COLOR = (93, 216, 228)

SPEED = 10

# Global variables
pygame.init()
screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock: pygame.time.Clock = pygame.time.Clock()
pygame.display.set_caption('Snake Game')


class GameObject:
    """Base class for game objects."""

    def __init__(self, position=CENTER_POSITION, body_color=SNAKE_COLOR):
        """
        Initialize basic attributes.
        :param position: Object position (tuple)
        :param body_color: Object color (RGB tuple)
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Draw a single cell on the surface."""
        if color is None:
            color = self.body_color
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Class for the apple."""

    def __init__(self, position=CENTER_POSITION, body_color=APPLE_COLOR, occupied_positions=None):
        """Initialize the apple."""
        super().__init__(position=position, body_color=body_color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Set a random position for the apple avoiding occupied positions."""
        while True:
            new_position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self):
        """Draw the apple."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Class for the snake."""

    def __init__(self, position=CENTER_POSITION, body_color=SNAKE_COLOR):
        """Initialize the snake."""
        super().__init__(position=position, body_color=body_color)
        self.reset()

    def reset(self):
        """Reset the snake to its initial state."""
        self.length = 1
        self.positions = [self.position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Get the position of the snake's head."""
        return self.positions[0]

    def move(self):
        """Update the snake's position."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop() if len(self.positions) > self.length else None

    def grow(self):
        """Increase the snake's length."""
        self.length += 1

    def update_direction(self):
        """Update the snake's direction."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Draw the entire snake."""
        for position in self.positions:
            self.draw_cell(position)

        if self.last:
            self.draw_cell(self.last, BACKGROUND_COLOR)
            self.draw_cell(self.last, BACKGROUND_COLOR)


DIRECTION_MAP = {
    (LEFT, pygame.K_UP): UP,
    (RIGHT, pygame.K_UP): UP,
    (UP, pygame.K_LEFT): LEFT,
    (DOWN, pygame.K_LEFT): LEFT,
    (UP, pygame.K_RIGHT): RIGHT,
    (DOWN, pygame.K_RIGHT): RIGHT,
    (LEFT, pygame.K_DOWN): DOWN,
    (RIGHT, pygame.K_DOWN): DOWN,
}

def handle_keys(snake):
    """Handle key presses."""
    opposite_direction = (-snake.direction[0], -snake.direction[1])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            else:
                snake.next_direction = DIRECTION_MAP.get((snake.direction, event.key), snake.direction)


def main():
    """Main game loop."""
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    MAX_ITERATIONS = 1000  # To prevent infinite loop during tests
    iteration = 0  # For debugging purposes

    while iteration <= MAX_ITERATIONS:
        screen.fill(BACKGROUND_COLOR)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Check for collisions with itself
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()

        pygame.display.update()
        clock.tick(SPEED)
        iteration += 1


if __name__ == '__main__':
    main()

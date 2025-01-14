import random
import sys

import pygame

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

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
    """Base class for all game objects."""

    def draw(self):
        """Abstract method for drawing the object"""
        raise NotImplementedError('Subclasses must implement this method.')

    def __init__(self, position=CENTER_POSITION, body_color=SNAKE_COLOR):
        """Initialize the object with its position and color.

        Args:
            position (tuple): The (x, y) position of the object.
            body_color (tuple): The RGB color of the object.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Draw a single cell on the game screen.

        Args:
            position (tuple): The (x, y) position of the cell.
            color (tuple, optional): The RGB color of the cell.
                Defaults to object's body color.
        """
        if color is None:
            color = self.body_color
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)


class Apple(GameObject):
    """Class representing the apple in the game."""

    def __init__(self, position=CENTER_POSITION, body_color=APPLE_COLOR,
                 occupied_positions=None):
        """Initialize the apple with its position and color.

        Args:
            position (tuple): The initial position of the apple.
            body_color (tuple): The RGB color of the apple.
            occupied_positions (list, optional): List of positions that the
                apple should avoid. Defaults to None.
        """
        super().__init__(position=position, body_color=body_color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Set a random position for the apple avoiding occupied positions.

        Args:
            occupied_positions (list): List of positions that the apple
                should avoid.
        """
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Draw the apple on the game screen."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Class representing the snake in the game."""

    def __init__(self, position=CENTER_POSITION, body_color=SNAKE_COLOR):
        """Initialize the snake with its initial position and color.

        Args:
            position (tuple): The initial position of the snake.
            body_color (tuple): The RGB color of the snake.
        """
        super().__init__(position=position, body_color=body_color)
        self.reset(initial_direction=RIGHT)

    def reset(self, initial_direction=None):
        """Reset the snake to its initial state.

        Args:
            initial_direction (tuple, optional): The initial direction of the snake.
                Defaults to a random direction.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = initial_direction if initial_direction else random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Get the position of the snake's head.

        Returns:
            tuple: The (x, y) position of the head.
        """
        return self.positions[0]

    def move(self):
        """Update the snake's position by moving in the current direction."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def grow(self):
        """Increase the length of the snake."""
        self.length += 1

    def update_direction(self):
        """Update the snake's direction based on the next direction."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Draw the entire snake on the game screen."""
        for position in self.positions:
            self.draw_cell(position)

        if self.last:
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
    """Handle key presses for controlling the snake.

    Args:
        snake (Snake): The snake object to control.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            else:
                snake.next_direction = DIRECTION_MAP.get(
                    (snake.direction, event.key), snake.direction
                )


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
            apple.randomize_position(snake.positions)

        elif snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()

        pygame.display.update()
        clock.tick(SPEED)
        iteration += 1


if __name__ == '__main__':
    main()

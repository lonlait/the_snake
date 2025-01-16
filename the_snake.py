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
    """
    Base class for all game objects in the game. Defines
    common properties and methods for rendering objects.
    """

    def draw(self):
        """
        Draw the object on the game screen. This method
        must be overridden by subclasses.
        """
        raise NotImplementedError('Subclasses must implement this method.')

    def __init__(self, position=CENTER_POSITION, body_color=SNAKE_COLOR):
        """
        Initialize the game object with a position and color.

        Args:
            position (tuple): The (x, y) position of the object.
            body_color (tuple): The RGB color of the object.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """
        Draw a single cell on the screen.

        Args:
            position (tuple): The (x, y) position of the cell.
            color (tuple, optional): The color of the cell. Defaults
            to the object's color.
        """
        color = color or self.body_color
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        if color != BACKGROUND_COLOR:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """
    Class representing the apple in the game. Apples serve
    as a goal for the snake to grow.
    """

    def __init__(self, position=CENTER_POSITION, body_color=APPLE_COLOR,
                 occupied_positions=None):
        """
        Initialize the apple with a position, color, and
        list of occupied positions to avoid.

        Args:
            position (tuple): The starting position of the apple.
            body_color (tuple): The RGB color of the apple.
            occupied_positions (list, optional): List of positions
            the apple should avoid.
        """
        super().__init__(position=position, body_color=body_color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(self, occupied_positions):
        """
        Generate a random position for the apple, ensuring it
        does not overlap with occupied positions.

        Args:
            occupied_positions (list): Positions to avoid.
        """
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Render the apple on the game screen."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """
    Class representing the snake in the game. The snake grows
    by eating apples and must avoid collisions with itself.
    """

    def __init__(self, position=CENTER_POSITION, body_color=SNAKE_COLOR):
        """
        Initialize the snake with a starting position and color.

        Args:
            position (tuple): The initial position of the snake.
            body_color (tuple): The RGB color of the snake.
        """
        super().__init__(position=position, body_color=body_color)
        self.reset()

    def reset(self, initial_direction=None):
        """
        Reset the snake to its initial state, with a length
        of 1 and a random direction.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = initial_direction or random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """
        Get the position of the snake's head.

        Returns:
            tuple: The (x, y) position of the head.
        """
        return self.positions[0]

    def move(self):
        """
        Update the snake's position by moving its head in
        the current direction. The movement wraps around
        screen boundaries.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def grow(self):
        """Increase the length of the snake by one."""
        self.length += 1

    def update_direction(self):
        """
        Update the snake's direction to the next direction
        if it is set.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """
        Render the snake on the game screen, drawing each
        segment of its body.
        """
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
    """
    Handle keyboard input to control the snake's direction.
    Pressing escape exits the game.

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
    """
    Main game loop. Initializes game objects and runs
    the game logic and rendering in a loop.
    """
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    max_iterations = 1000
    iteration = 0

    while iteration <= max_iterations:
        screen.fill(BACKGROUND_COLOR)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset(initial_direction=RIGHT)
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

import pygame
import math


# rotation implemented with help from:
# https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
def alt_rotate(image, pos, origin_pos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    return rotated_image, rotated_image_rect


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, position, car_type, window):
        pygame.sprite.Sprite.__init__(self)

        # image and rendering
        self.window = window
        self.position = position
        self.original_size = 950
        self.scale = 0.05  # TODO: Fix scaling of turning to be more fun
        self.image_clean = pygame.image.load(f'assets/image/car_{car_type}.png').convert_alpha()
        self.aspect_ratio = self.image_clean.get_width() / self.image_clean.get_height()
        self.image_clean = pygame.transform.scale(self.image_clean,
                                                  (int(self.original_size * self.scale * self.aspect_ratio),
                                                   int(self.original_size * self.scale)))  # (width, height)
        self.clean_rect = self.image_clean.get_rect(center=self.position)
        self.image = self.image_clean
        self.rect = self.image.get_rect(center=self.position)
        self.angle = 0

        self.front_vec_length = 50
        self.tire_direction = None  # TODO change turning to match tire direction, turning radius, tire animation
        self.vel = 0
        self.x_vel = 0
        self.y_vel = 0

        # Tune these parameters for feel
        self.max_vel = 69
        self.max_reverse_vel = -self.max_vel / 3
        self.acceleration = 3  # in pixels per frame per frame
        self.braking_level = 2
        self.friction_coeff = 1.5
        self.turn_rate = 0.7

        self.accelerating = False
        self.braking = False
        self.emergency_braking = False
        self.turning_left = False
        self.turning_right = False

        self.dir = [75, 75]  # initial direction
        # TODO: make this not hard-coded to allow different car spawn orientations
        # DEBUG
        self.count = 0

    def update(self):
        self.move()
        self.dir = [math.sin(self.angle / 180 * math.pi),
                    math.cos(self.angle / 180 * math.pi)]  # Why... why / 180 * math.pi?
        # Apply friction, stop at low speed
        if self.vel > 2 * self.scale:
            self.vel -= self.friction_coeff
        if self.vel < -2 * self.scale:
            self.vel += self.friction_coeff
        elif not self.accelerating and 0 < self.vel <= 2 * self.scale:
            self.vel = 0
        elif not self.braking and -2 * self.scale <= self.vel < 0:
            self.vel = 0

        self.x_vel = self.vel * self.dir[0]
        self.y_vel = self.vel * self.dir[1]

        # Check for max vel and update position with vel
        self.position[0] += self.x_vel
        self.position[1] += self.y_vel

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]

        self.image, self.rect = alt_rotate(self.image_clean, self.position,
                                           (self.image_clean.get_width() // 2, self.image_clean.get_height() // 2),
                                           self.angle)
        self.draw()

    def draw(self):
        self.window.blit(self.image, self.rect)

    def move(self):
        if self.turning_left and self.vel != 0:
            self.angle += self.turn_rate * (1 / self.scale) * 1 + -(self.vel / self.max_vel)
            # DEBUG
            # if self.count % 24 == 0:
            #     print(1 + -(self.vel / self.max_vel))
        if self.turning_right and self.vel != 0:
            self.angle -= self.turn_rate * (1 / self.scale) * 1 + -(self.vel / self.max_vel)
        if self.accelerating:
            if self.vel + self.acceleration <= self.max_vel:
                self.vel += self.acceleration
        if self.braking:
            if self.vel - self.braking_level >= self.max_reverse_vel:
                self.vel -= self.braking_level

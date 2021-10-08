# This is a sample Python script.
import math
import pygame

pygame.init()

SCREEN_HEIGHT = 900
SCREEN_WIDTH = 1500
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("project-rc")

clock = pygame.time.Clock()
FPS = 30

# Colors as always via https://coolors.co
GREEN = '#0FA98F'  # "zomp" green


def blitRotate(image, pos, originPos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    return rotated_image, rotated_image_rect
    # # rotate and blit the image
    # surf.blit(rotated_image, rotated_image_rect)

    # draw rectangle around the image
    # pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()), 2)


class Car(pygame.sprite.Sprite):
    def __init__(self, position, mass, car_type, orientation):
        pygame.sprite.Sprite.__init__(self)

        # image and rendering
        self.position = position
        self.original_size = 150
        self.scale = 0.5
        self.image_clean = pygame.image.load(f'assets/image/car_{car_type}.png').convert_alpha()
        self.aspect_ratio = self.image_clean.get_width() / self.image_clean.get_height()
        self.image_clean = pygame.transform.scale(self.image_clean,
                                                  (int(self.original_size * self.scale * self.aspect_ratio), int(self.original_size * self.scale)))  # (width, height)
        self.clean_rect = self.image_clean.get_rect(center=self.position)
        self.image = self.image_clean
        self.rect = self.image.get_rect(center=self.position)
        self.mass = mass # TODO implement physical modelling of behavior
        self.angle = 0

        self.front_vec_length = 75
        self.tire_direction = None  # TODO change turning to match tire direction, turning radius, tire animation
        self.vel = 0
        self.x_vel = 0
        self.y_vel = 0
        self.max_vel = 75 * self.scale
        self.max_reverse_vel = -self.max_vel / 3
        self.acceleration = 3 * self.scale  # in pixels per frame per frame
        self.braking_level = 2 * self.scale
        self.friction_coeff = 1.5 * self.scale
        self.accelerating = False
        self.braking = False
        self.turn_rate = 3
        self.turning_left = False
        self.turning_right = False

        self.dir = [75, 75]  # initial direction TODO: make this not hard-coded to allow different car spawn orientations
        # DEBUG
        self.count = 0


    def update(self):
        self.move()
        self.dir = [math.sin(self.angle / 180 * math.pi), math.cos(self.angle / 180 * math.pi)]  # Why... why / 180 * math.pi?
        # Apply friction, stop at low speed
        if self.vel > 2  * self.scale:
            self.vel -= self.friction_coeff
        if self.vel < -2  * self.scale:
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

        self.image, self.rect = blitRotate(self.image_clean, self.position,
                                           (self.image_clean.get_width() // 2, self.image_clean.get_height() // 2), self.angle)
        self.draw()

    def draw(self):
        window.blit(self.image, self.rect)

    def move(self):
        if self.turning_left and self.vel != 0:
            self.angle += self.turn_rate * (1 / self.scale) * 1 + -(self.vel/self.max_vel)
            if self.count % 24 == 0:
                print(1 + -(self.vel/self.max_vel))
        if self.turning_right and self.vel != 0:
            self.angle -= self.turn_rate * (1 / self.scale) * 1 + -(self.vel/self.max_vel)
        if self.accelerating:
            if self.vel + self.acceleration <= self.max_vel:
                self.vel += self.acceleration
        if self.braking:
            if self.vel - self.braking_level >= self.max_reverse_vel:
                self.vel -= self.braking_level


player = Car([100, 100], 10, "purple", None)
run = True
while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                player.turning_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player.turning_right = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.accelerating = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                player.braking = True
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.turning_left = False
            if event.key == pygame.K_d:
                player.turning_right = False
            if event.key == pygame.K_w:
                player.accelerating = False
            if event.key == pygame.K_s:
                player.braking = False

    window.fill(GREEN)
    pygame.draw.line(window, [0, 0, 0], player.rect.center, (player.rect.centerx + player.dir[0],  player.rect.centery + player.dir[1]))

    player.update()

    # DEBUG
   # pygame.draw.line(window, [255, 0, 0], player.rect.center, (int(player.rect.centerx + math.sin(player.angle) * 2), int(player.rect.centery + math.cos(player.angle)) * 2))
    pygame.draw.circle(window, [0,0,0], player.rect.center, 75  * player.scale, 2)

    pygame.display.update()

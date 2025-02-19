import math
import pygame
import sys

class Body:
    def __init__(self, name, mass, x, y, vx, vy, color, radius):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0.0
        self.ay = 0.0
        self.color = color
        self.radius = radius

    def update_velocity(self, dt):
        self.vx += self.ax * dt
        self.vy += self.ay * dt

    def update_position(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

# Constants
G = 4 * math.pi**2  # AU³/(Msun yr²)
SCALE = 10  # pixels per AU
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH//2, HEIGHT//2)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)

# Create celestial bodies with realistic colors and relative sizes
sun = Body("Sun", 1.0, 0.0, 0.0, 0.0, 0.0, (255, 255, 0), 20)

planets_data = [
    ("Mercury", 1.65e-7, 0.387, (150, 150, 150), 8),
    ("Venus", 2.45e-6, 0.723, (255, 165, 0), 10),
    ("Earth", 3.0e-6, 1.0, (0, 0, 255), 12),
    ("Mars", 3.3e-7, 1.524, (255, 0, 0), 9),
    ("Jupiter", 9.5e-4, 5.2, (255, 215, 0), 15),
    ("Saturn", 2.75e-4, 9.5, (210, 180, 140), 14),
    ("Uranus", 4.4e-5, 19.2, (173, 216, 230), 13),
    ("Neptune", 5.15e-5, 30.1, (0, 0, 150), 13)
]

bodies = [sun]
for name, mass, r, color, size in planets_data:
    vy = 2 * math.pi / math.sqrt(r)
    bodies.append(Body(name, mass, r, 0.0, 0.0, vy, color, size))

# Adjust Sun's velocity to maintain system momentum
total_px = sum(p.mass * p.vx for p in bodies if p != sun)
total_py = sum(p.mass * p.vy for p in bodies if p != sun)
sun.vy = -total_py / sun.mass

def compute_accelerations(bodies):
    for body in bodies:
        body.ax = 0.0
        body.ay = 0.0
        
    for i in range(len(bodies)):
        body_i = bodies[i]
        for j in range(len(bodies)):
            if i == j:
                continue
            body_j = bodies[j]
            dx = body_j.x - body_i.x
            dy = body_j.y - body_i.y
            r = math.hypot(dx, dy)
            if r == 0:
                continue
            factor = G * body_j.mass / r**3
            body_i.ax += factor * dx
            body_i.ay += factor * dy

# Simulation parameters
dt = 0.01  # Time step in years
speed_factor = 5  # Speed multiplier
paused = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_q:
                running = False

    screen.fill((0, 0, 0))

    if not paused:
        compute_accelerations(bodies)
        for body in bodies:
            body.update_velocity(dt * speed_factor)
            body.update_position(dt * speed_factor)

    # Draw orbits and bodies
    for body in bodies:
        if body != sun:
            # Convert AU to screen coordinates
            x = int(body.x * SCALE) + CENTER[0]
            y = -int(body.y * SCALE) + CENTER[1]  # Invert y-axis
            pygame.draw.circle(screen, (50, 50, 50), (x, y), int(body.radius/2), 1)
            
        # Draw body
        x = int(body.x * SCALE) + CENTER[0]
        y = -int(body.y * SCALE) + CENTER[1]
        pygame.draw.circle(screen, body.color, (x, y), body.radius)

    # Draw UI
    status_text = font.render(f"Speed: {speed_factor}x [UP/DOWN] | {'Paused' if paused else 'Running'} [SPACE]", 
                            True, (255, 255, 255))
    screen.blit(status_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
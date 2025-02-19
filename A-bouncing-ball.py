import pygame
import sys
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")
clock = pygame.time.Clock()

# ----- Simulation Parameters -----
hexagon_center = (WIDTH // 2, HEIGHT // 2)
hexagon_radius = 250       # distance from center to each vertex
hexagon_angle = 0          # starting rotation (radians)
hexagon_angular_speed = 0.5  # radians per second

ball_radius = 15
ball_position = [WIDTH // 2, HEIGHT // 2 - 100]  # start near center, slightly above
ball_velocity = [100, 0]  # initial velocity (px/s)

gravity = 500  # gravitational acceleration (px/s^2, downward)
restitution = 0.9  # coefficient of restitution (bounciness)
friction = 0.2     # friction coefficient (reduces tangential velocity on impact)

# ----- Helper Functions -----
def get_hexagon_vertices(center, radius, angle):
    """Compute the vertices of a regular hexagon rotated by 'angle'."""
    vertices = []
    for i in range(6):
        theta = angle + i * (2 * math.pi / 6)
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        vertices.append((x, y))
    return vertices

def check_collision_and_resolve(ball_pos, ball_vel, vertices, hex_center, ang_speed, restitution, friction):
    """
    Check the ball against each hexagon edge.
    For each edge we:
      1. Compute its inward normal.
      2. Find the closest point on the edge (clamped to the segment).
      3. If the ball overlaps the wall (distance < ball radius) and is moving inward,
         adjust the ball’s velocity (taking into account the wall’s local velocity due to rotation)
         and push it out.
    Returns True if a collision was resolved.
    """
    collided = False

    for i in range(len(vertices)):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % len(vertices)]
        # Edge vector and unit vector along the edge:
        edge_vec = (p2[0] - p1[0], p2[1] - p1[1])
        edge_length = math.hypot(edge_vec[0], edge_vec[1])
        if edge_length == 0:
            continue
        edge_unit = (edge_vec[0] / edge_length, edge_vec[1] / edge_length)

        # Compute candidate normal (rotate edge_unit 90°)
        normal = (-edge_unit[1], edge_unit[0])
        # Ensure the normal points inward. Check using the midpoint of the edge.
        midpoint = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        to_center = (hex_center[0] - midpoint[0], hex_center[1] - midpoint[1])
        if (normal[0] * to_center[0] + normal[1] * to_center[1]) < 0:
            normal = (-normal[0], -normal[1])

        # Find the closest point on the segment to the ball’s center:
        ball_to_p1 = (ball_pos[0] - p1[0], ball_pos[1] - p1[1])
        t = ball_to_p1[0] * edge_unit[0] + ball_to_p1[1] * edge_unit[1]
        t_clamped = max(0, min(edge_length, t))
        closest_point = (p1[0] + edge_unit[0] * t_clamped, p1[1] + edge_unit[1] * t_clamped)

        # Determine distance from ball center to closest point:
        dist_vec = (ball_pos[0] - closest_point[0], ball_pos[1] - closest_point[1])
        dist = math.hypot(dist_vec[0], dist_vec[1])
        if dist < ball_radius:
            # Collision detected – compute penetration depth.
            penetration = ball_radius - dist

            # Avoid division by zero if the ball center exactly equals the contact point.
            if dist != 0:
                collision_normal = (dist_vec[0] / dist, dist_vec[1] / dist)
            else:
                collision_normal = normal

            # Compute the wall’s velocity at the contact point (due to hexagon rotation).
            # In 2D, a point at (x, y) relative to the center has velocity (-w*(y), w*(x)).
            wall_vel = (
                -ang_speed * (closest_point[1] - hex_center[1]),
                ang_speed * (closest_point[0] - hex_center[0])
            )

            # Compute the ball’s velocity relative to the moving wall:
            rel_vel = (ball_vel[0] - wall_vel[0], ball_vel[1] - wall_vel[1])
            rel_vel_normal = rel_vel[0] * collision_normal[0] + rel_vel[1] * collision_normal[1]

            # Only respond if the ball is moving into the wall.
            if rel_vel_normal < 0:
                # Decompose the relative velocity into normal and tangential parts.
                v_normal = (rel_vel_normal * collision_normal[0], rel_vel_normal * collision_normal[1])
                v_tangent = (rel_vel[0] - v_normal[0], rel_vel[1] - v_normal[1])
                # Reflect the normal component (with restitution) and damp the tangential component (with friction).
                new_v_normal = (-restitution * v_normal[0], -restitution * v_normal[1])
                new_v_tangent = ((1 - friction) * v_tangent[0], (1 - friction) * v_tangent[1])
                new_rel_vel = (new_v_normal[0] + new_v_tangent[0], new_v_normal[1] + new_v_tangent[1])
                # The new ball velocity is the new relative velocity plus the wall’s velocity.
                ball_vel[0] = new_rel_vel[0] + wall_vel[0]
                ball_vel[1] = new_rel_vel[1] + wall_vel[1]

                # Correct the ball’s position so it is no longer penetrating the wall.
                ball_pos[0] += collision_normal[0] * penetration
                ball_pos[1] += collision_normal[1] * penetration

                collided = True
                # Process one collision per check to avoid over-correction.
                break

    return collided

# ----- Main Loop -----
running = True
while running:
    dt = clock.tick(60) / 1000.0  # seconds elapsed since last frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the hexagon’s rotation.
    hexagon_angle += hexagon_angular_speed * dt
    vertices = get_hexagon_vertices(hexagon_center, hexagon_radius, hexagon_angle)

    # ----- Update Ball Physics -----
    # Apply gravity.
    ball_velocity[1] += gravity * dt
    # Update ball position.
    ball_position[0] += ball_velocity[0] * dt
    ball_position[1] += ball_velocity[1] * dt

    # Check for collisions with the hexagon walls.
    # Loop a few times to help resolve multiple (or deep) collisions.
    for _ in range(3):
        if not check_collision_and_resolve(
            ball_position, ball_velocity, vertices, hexagon_center,
            hexagon_angular_speed, restitution, friction
        ):
            break

    # ----- Rendering -----
    screen.fill((30, 30, 30))
    # Draw the rotating hexagon.
    pygame.draw.polygon(screen, (200, 200, 200), vertices, 3)
    # Draw the ball.
    pygame.draw.circle(screen, (255, 50, 50), (int(ball_position[0]), int(ball_position[1])), ball_radius)
    pygame.display.flip()

pygame.quit()
sys.exit()

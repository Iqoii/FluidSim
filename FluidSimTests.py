import pygame, random, math
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1600, 1000
search_radius = 30
search_radius_SQ = search_radius ** 2
mass = 1
VOLUME = math.pi * search_radius ** 4 / 6
SCALE = 12 / (math.pi * search_radius ** 4)
INERTIA = True
target_density = 0.7

volume = math.pi * math.pow(search_radius, 4)/6
scale = 12/ (math.pi* math.pow(search_radius, 4))

pressureMultiplier= 200

forces_dict = {}
slopes_dict = {}

# Colors
WHITE, BLACK, BLUE = (255, 255, 255), (0, 0, 0), (0, 0, 255)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fluid Sim")

# Particle class
class Particle:
    def __init__(self, x, y, radius, speed):
        self.x, self.y = x, y
        self.radius = radius
        self.speed_x, self.speed_y = speed
        self.gravity = 0
        self.acceleration = 0.1
        self.placeholder_x, self.placeholder_y = 0, 0

    def move(self, vector):
        if not INERTIA:
            self.speed_x, self.speed_y = vector
        else:
            self.speed_x += vector[0]
            self.speed_y += vector[1]

        self.speed_y += self.gravity
        self.x += self.speed_x
        self.y += self.speed_y

        # Boundary conditions
        if self.y + self.radius >= WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.radius
            self.speed_y = -abs(self.speed_y)
        elif self.y - self.radius <= 0:
            self.y = self.radius
            self.speed_y = abs(self.speed_y) * 0.1
        if self.x + self.radius >= WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.radius
            self.speed_x = -abs(self.speed_x)
        elif self.x - self.radius <= 0:
            self.x = self.radius
            self.speed_x = abs(self.speed_x)

    def draw(self, surface, color):
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

# Initialize particles
amount = 2000

particles_per_row = round(math.sqrt(amount))

particles_per_col = round((amount - 1) / particles_per_row + 1) - 1

spacing_x = 400 // (particles_per_col + 1)
spacing_y = 400 // (particles_per_row + 1)

spacing_x = 10
spacing_y = 10

particles = []

#Grid code
for i in range(int(particles_per_row)):
    for j in range(int(particles_per_col)):
        x = (j + 1) * spacing_x 

        y = (i + 1) * spacing_y 

        
        particles.append(Particle(540+x, 230+y, 5, (0, 0)))

amount = len(particles)

# Kernel functions
def kernel(search_radius, distance):
    return (search_radius - distance) * (search_radius - distance) / volume

    
def kernelDerivative(search_radius, distance):
    if distance >= search_radius:
        return 0

    return (distance - search_radius) * scale

def getNeighbors(point_x, point_y):
    neighbors = []
    real_neighbors = []
    
    row = max(int((point_y // search_radius)), 0)
    col = max(int((point_x // search_radius)), 0)
    #print("real col:", col, "real row", row)
    
    
    lim_i_x = max(col - 1, 0)
    lim_i_y = min(col + 1, GRID_COLS)
    lim_j_x = max(row - 1, 0)
    lim_j_y = min(row + 1, GRID_ROWS)

    for i in range(lim_i_x, lim_i_y+1):
        #print("col: ", i)
        for j in range(lim_j_x, lim_j_y+1):
            #print("row: ", j)
            # Check if indices are within the grid bounds
            if 0 <= i < GRID_COLS and 0 <= j < GRID_ROWS:
                neighbors.extend(grid[i][j])

    for neighbor in neighbors:
        dx = point_x - neighbor.x
        if abs(dx) > search_radius:
            continue
        
        dy = point_y - neighbor.y
        if abs(dy) == 0 and abs(dx) == 0:
            continue

        if abs(dy) < search_radius:
            real_neighbors.append(neighbor)

    return real_neighbors

def calculateDensity(point, neighbors):
    point_x = point[0]
    point_y = point[1]
    density = 0  
    
    #neighbors = getNeighbors(point_x, point_y)
    

    for particle in neighbors:
        
        dx = particle.x - point_x
        dy = particle.y - point_y
        if abs(dx) > search_radius or abs(dy) > search_radius:
            continue

        distance = math.dist((particle.x, particle.y), point)

        if distance in forces_dict.keys():
            influence = forces_dict[distance]
            density += influence * mass
            continue
        else:
            influence = kernel(search_radius, distance)
            forces_dict[distance] = influence

        density += influence * mass
        forces_dict[distance] = influence

    
    return density * 1000 +1


def calculateSharedPressure(density, otherDensity):
    pressureA = convertDensityToPressure(density)
    pressureB = convertDensityToPressure(otherDensity)
    return (pressureA + pressureB) / 2



def calculatePropertyGradient(point, i, neighbors):
    propertyGradient = [0, 0]
    point_x, point_y = point.x, point.y
    density = densities[i]
    
   

    #TO DO: Add the second density properly for the shared pressure 
    for particle in neighbors:
        dx = point_x - particle.x
        dy = point_y - particle.y
    
        distance_sq = dx ** 2 + dy ** 2
        

        if distance_sq == 0:
            continue

        distance = round(math.sqrt(distance_sq), 2)
        distance = max(0.001, distance)
        

        if distance in slopes_dict.keys():
            slope = slopes_dict[distance]
           
        else:
            slope = kernelDerivative(search_radius, distance)
            slopes_dict[distance] = slope
            


        direction_x, direction_y = dx / distance, dy / distance
        

     
            
        pressure = calculateSharedPressure(density, density)
        
        

        value = -pressure * slope * mass

        propertyGradient[0] += value * direction_x / density
        propertyGradient[1] += value * direction_y / density

        
    
        
    #print("Property Gradient: ", propertyGradient)
    return propertyGradient


def convertDensityToPressure(density):
    deltaDensity = density - target_density
    pressure = deltaDensity * pressureMultiplier
    return pressure





# Main loop

running = True
mouse_pressed = False
stop = False

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:  # Stop particles
                for particle in particles:
                    particle.placeholder_x, particle.placeholder_y = particle.speed_x, particle.speed_y
                    particle.speed_x, particle.speed_y = 0, 0
                    stop = True
            if event.key == pygame.K_1:  # Resume particles
                for particle in particles:
                    particle.speed_x, particle.speed_y = particle.placeholder_x, particle.placeholder_y
                    stop = False
            if event.key == pygame.K_2:  # Enable gravity
                for particle in particles:
                    particle.gravity = 1.5
            if event.key == pygame.K_3:  # Disable gravity
                for particle in particles:
                    particle.gravity = 0
            if event.key == pygame.K_4:  # Set pressure multiplier to 200
                PRESSURE_MULTIPLIER = 200
                INERTIA = True
            if event.key == pygame.K_5:  # Set pressure multiplier to 500
                PRESSURE_MULTIPLIER = 500
                INERTIA = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pressed = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                mouse_pressed = False

    # Handle mouse interaction
    if mouse_pressed:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for particle in particles:
            distance = math.hypot(particle.x - mouse_x, particle.y - mouse_y)
            if distance < 50:  # Repel particles within a radius
                force_magnitude = 100000 / (distance ** 2 + 1)
                force_x = force_magnitude * (mouse_x - particle.x) / distance
                force_y = force_magnitude * (mouse_y - particle.y) / distance
                particle.speed_x -= force_x
                particle.speed_y -= force_y
                # Limit speed
                max_speed = 15
                speed = math.hypot(particle.speed_x, particle.speed_y)
                if speed > max_speed:
                    particle.speed_x = (particle.speed_x / speed) * max_speed
                    particle.speed_y = (particle.speed_y / speed) * max_speed

    # Update grid for neighbor search
    GRID_ROWS = WINDOW_HEIGHT // search_radius
    GRID_COLS = WINDOW_WIDTH // search_radius
    grid = [[[] for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

    for particle in particles:
        row = min(max(int(particle.y // search_radius), 0), GRID_ROWS - 1)
        col = min(max(int(particle.x // search_radius), 0), GRID_COLS - 1)
        grid[col][row].append(particle)

    # Calculate densities and forces
    if not stop:
        densities = []
        neighbors = []
        predicted_positions = []

        for i in range(amount):
            particle = particles[i]
            predicted_x = particle.x + particle.speed_x
            predicted_y = particle.y + particle.speed_y
            predicted_positions.append((predicted_x, predicted_y))
            neighbors.append(getNeighbors(predicted_x, predicted_y))
            densities.append(calculateDensity((predicted_x, predicted_y), neighbors[i]))

        pressure_acceleration = []
        for i in range(amount):
            pressure_force = calculatePropertyGradient(particles[i], i, neighbors[i])
            pressure_acceleration.append([
                pressure_force[0] / densities[i] * 1000,
                pressure_force[1] / densities[i] * 1000
            ])

        # Move particles
        for i in range(amount):
            particles[i].move(pressure_acceleration[i])

    # Draw particles
    screen.fill(WHITE)
    for particle in particles:
        particle.draw(screen, BLUE)
    pygame.display.flip()

    # Cap frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()

from yade import pack, utils, ymport, qt, plot
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import csv

# Initialize simulation
O.reset()
O.periodic = True  # Enable periodic boundaries

# Define parameters
num_particles = 26  # Number of particles in each dimension
radius = 0.05  # Radius of each particle
gap = 0  # Gap between particles
square_size = num_particles * (radius * 2 + gap)  # Total size of the square
dist = 2 * radius + gap

# Create a square arrangement of particles
for i in range(num_particles):
    for j in range(num_particles):
        x = i * dist
        y = j * dist
        z = -1.5 * radius
        body = utils.sphere((x, y, z), radius)
        
        if (i == num_particles // 2 ) and j == 0:  # Apply force to the particle
            body.shape.color = (1, 0, 0)  # Highlight the particle in red
            O.bodies.append(body)
            O.forces.addF(body.id, (0, 10000, 0))
        elif j == 25:
            body.shape.color = (0, 1, 0)  # Highlight the particles in green
            O.bodies.append(body)
        else:
            body.shape.color = (1, 1, 1)  # Set color to white for other spheres
            O.bodies.append(body)

# Define interactions
O.engines = [
    ForceResetter(),
    InsertionSortCollider([Bo1_Sphere_Aabb()]),
    InteractionLoop(
        [Ig2_Sphere_Sphere_ScGeom()],
        [Ip2_FrictMat_FrictMat_FrictPhys()],
        [Law2_ScGeom_FrictPhys_CundallStrack()]
    ),
    NewtonIntegrator(gravity=(0, 0, 0), damping=0.0),
    PyRunner(command='record_positions()', iterPeriod=10)  # Adjusted to run every 10 time steps
]

# Set periodic boundary vectors
O.cell.setBox((square_size, square_size, square_size))

# Set material properties
O.materials.append(FrictMat(young=62.7e9, poisson=0.2, frictionAngle=radians(28.1)))

# Set time step
O.dt = 0.5 * utils.PWaveTimeStep()

# Lists to store particle positions over time
positions = []

# Initialize CSV file
csv_filename = 'particle_positions.csv'
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Particle ID', 'X Position', 'Y Position', 'Time'])

# Function to record the positions of green particles
def record_positions():
    if O.iter % 50000 == 0:  # Skip 10 time steps
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for body in O.bodies:
                if isinstance(body.shape, Sphere) and body.shape.color == (0, 1, 0):
                    pos = body.state.pos
                    positions.append((pos[0], pos[1], O.time))
                    writer.writerow([body.id, pos[0], pos[1], O.time])

# Initialize the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X Position')
ax.set_ylabel('Y Position')
ax.set_zlabel('Time')
ax.set_title('Positions of Green Particles Over Time')

# Set axis limits to ensure the particles remain visible
ax.set_xlim([0, num_particles * dist])
ax.set_ylim([0, num_particles * dist])
ax.set_zlim([0, O.dt * 3000000])

# Function to update the plot
def update_plot(i):
    ax.clear()
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Time')
    ax.set_title('Positions of Green Particles Over Time')
    ax.set_xlim([0, num_particles * dist])
    ax.set_ylim([0, num_particles * dist * 3])
    ax.set_zlim([0, O.dt * 3000000])
    
    if positions:
        x, y, z = zip(*positions)
        ax.plot(x, y, z, linestyle='-', color='g', linewidth=0.5, label='Green Particles')
        ax.scatter(x, y, z, color='g')  # Add markers
    ax.legend()

# Set up animation with updates every few seconds
ani = FuncAnimation(fig, update_plot, interval=2000)  # Update every 2 seconds

# Run the simulation
O.run(50000, True)

# Show the plot
plt.show()

# Start Yade's graphical interface
qt.View()
qt.Controller()

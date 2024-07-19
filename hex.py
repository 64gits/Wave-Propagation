from yade import pack, utils, ymport, qt, plot
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import math

# Initialize simulation
O.reset()
O.periodic = True  # Enable periodic boundaries

# Define parameters
r3 = math.sqrt(3)
num_particles = 26  # Number of particles in each dimension
radius = 1  # Radius of each particle
gap = 0  # Gap between particles
square_size1 = num_particles * (radius * 2 + gap) * radius # Total size of the square
#square_size2 = (2*(num_particles * radius) + radius * r3)+ 2* radius
square_size2 = 31*r3 + 2
dist = 2 * radius + gap

# Create a square arrangement of particles
for i in range(0,num_particles):
    j = 0
    while j < num_particles:
    #for j in range(0,num_particles, r3 * radius):
        x = i * dist
        y = j * dist
        z = -2.2 * radius
        body = utils.sphere((x, y, z), radius)
        bodyy = utils.sphere((x + radius, y + r3 * radius, z), radius)
        bodyy.shape.color = (1, 1, 1)
        O.bodies.append(bodyy)
        if (i == num_particles // 3 or i == (num_particles // 3)*2) and j == 0:  # Apply force to the particle
            body.shape.color = (1, 0, 0)  # Highlight the particle in red
            O.bodies.append(body)
            O.forces.addF(body.id, (0, 1000000, 0))
        elif j == radius * r3 * (10):
            body.shape.color = (0, 1, 0)  # Highlight the particles in green
            O.bodies.append(body)
        else:
            body.shape.color = (1, 1, 1)  # Set color to white for other spheres
            O.bodies.append(body)
            
        j = j + (r3 * radius)

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
    PyRunner(command='record_positions()', iterPeriod=100)
]

# Set periodic boundary vectors
O.cell.setBox((square_size1, square_size2, square_size1))

# Set material properties
O.materials.append(FrictMat(young=62.7e9, poisson=0.2, frictionAngle=radians(28.1)))

# Set time step
O.dt = 0.5 * utils.PWaveTimeStep()

# Lists to store particle positions over time
time_steps = []
x_positions = []
y_positions = []

# Function to record the positions of green particles
def record_positions():
    for body in O.bodies:
        if isinstance(body.shape, Sphere) and body.shape.color == (0, 1, 0):
            pos = body.state.pos
            time_steps.append(O.time)
            x_positions.append(pos[0])
            y_positions.append(pos[1])

# Initialize the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter([], [], [], c='g', label='Green Particles')
ax.set_xlabel('X Position')
ax.set_ylabel('Y Position')
ax.set_zlabel('Time')
ax.set_title('Positions of Green Particles Over Time')
ax.legend()

# Set axis limits to ensure the particles remain visible
ax.set_xlim([0, num_particles * dist])
ax.set_ylim([0, num_particles * dist*2])
ax.set_zlim([0, O.dt * 3000000])

# Function to update the plot
def update_plot(i):
    sc._offsets3d = (x_positions, y_positions, time_steps)
    plt.draw()

# Set up animation with updates every few seconds
ani = FuncAnimation(fig, update_plot, interval=2000)  # Update every 2 seconds

# Run the simulation
O.run(1000, True)

# Show the plot
plt.show()

# Start Yade's graphical interface
qt.View()
qt.Controller()

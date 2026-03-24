import numpy as np

def metropolis_mc(n_particles, box_size, diameter, temperature, steps):
    positions = np.random.rand(n_particles, 2) * box_size
    acceptance_rate = 0
    for _ in range(steps):
        for i in range(n_particles):
            old_position = positions[i].copy()
            new_position = old_position + np.random.uniform(-0.1, 0.1, 2)
            if np.linalg.norm(new_position - old_position) < 0.1:
                positions[i] = new_position
                acceptance_rate += 1
    return positions, acceptance_rate / (n_particles * steps)
import numpy as np

def initialize_lattice(N, box_size, d0, seed=None):
    """
    Initializes particles in a square lattice configuration.
    N: Number of particles
    box_size: Size of the 2D box (e.g., 1.0)
    d0: Particle diameter
    seed: Random seed for reproducibility
    Returns: numpy array of particle positions
    """
    if seed is not None:
        np.random.seed(seed)

    # Calculate number of particles per side
    n_side = int(np.ceil(np.sqrt(N)))
    if n_side * n_side < N:
        raise ValueError("Cannot place N particles in a square lattice with current n_side calculation.")

    # Calculate spacing
    spacing = box_size / n_side

    positions = []
    for i in range(n_side):
        for j in range(n_side):
            if len(positions) < N:
                # Place particle in the center of its cell
                x = (i + 0.5) * spacing
                y = (j + 0.5) * spacing
                positions.append([x, y])
    
    positions = np.array(positions)

    # Check for initial overlaps based on d0
    # This check assumes d0 is set such that no overlaps occur in the initial lattice.
    # The actual check for overlaps needs to be done with the calculate_distance and check_overlap functions later.
    # For now, we assume the lattice generation itself ensures no overlap if d0 is appropriately chosen for the density.
    
    return positions

def calculate_distance(p1, p2, box_size):
    """
    Calculates the minimum distance between two particles using periodic boundary conditions.
    p1, p2: 2D numpy arrays representing particle positions
    box_size: Size of the 2D box
    Returns: float, minimum distance
    """
    delta = p1 - p2
    # Apply periodic boundary conditions
    delta = delta - box_size * np.round(delta / box_size)
    return np.sqrt(np.sum(delta**2))

def check_overlap(positions, current_particle_idx, new_position, d0, box_size):
    """
    Checks if a new_position for current_particle_idx overlaps with any other particle.
    positions: numpy array of all particle positions
    current_particle_idx: Index of the particle being moved
    new_position: Proposed new 2D position for the particle
    d0: Particle diameter
    box_size: Size of the 2D box
    Returns: bool, True if overlap, False otherwise
    """
    N = positions.shape[0]
    for i in range(N):
        if i == current_particle_idx:
            continue
        
        distance = calculate_distance(new_position, positions[i], box_size)
        if distance < d0:
            return True # Overlap
    return False # No overlap

def monte_carlo_step(positions, d0, box_size, alpha, rng):
    """
    Performs one Monte Carlo step (attempts to move one particle).
    positions: numpy array of all particle positions
    d0: Particle diameter
    box_size: Size of the 2D box
    alpha: Maximum displacement for a proposed move
    rng: numpy random number generator
    Returns: new positions array, boolean indicating if move was accepted
    """
    N = positions.shape[0]
    # Randomly select a particle
    particle_idx = rng.integers(N) 
    current_position = positions[particle_idx].copy()

    # Propose a random displacement
    displacement = (rng.random(2) - 0.5) * 2 * alpha # Corrected: use random(2) instead of rand(2)
    new_position = current_position + displacement

    # Apply periodic boundary conditions to the new position
    new_position = new_position % box_size

    # Check for overlap
    if not check_overlap(positions, particle_idx, new_position, d0, box_size):
        # No overlap, accept the move
        new_positions = positions.copy()
        new_positions[particle_idx] = new_position
        return new_positions, True
    else:
        # Overlap, reject the move
        return positions, False

def run_simulation(N, d0, box_size, alpha, n_cycles, n_equilibration_cycles, seed=None):
    """
    Runs the Monte Carlo simulation.
    N: Number of particles
    d0: Particle diameter
    box_size: Size of the 2D box
    alpha: Maximum displacement for a proposed move
    n_cycles: Total number of Monte Carlo cycles (1 cycle = N attempts to move a particle)
    n_equilibration_cycles: Number of cycles for equilibration
    seed: Random seed for reproducibility
    Returns: tuple (final_positions, acceptance_rate, sampled_positions)
    """
    rng = np.random.default_rng(seed)

    # Step 1: Initialization
    positions = initialize_lattice(N, box_size, d0, seed)

    # Store acceptance counts
    accepted_moves = 0
    total_moves = 0

    sampled_positions = []

    for cycle in range(n_cycles):
        for _ in range(N): # N attempts per cycle
            total_moves += 1
            new_positions, accepted = monte_carlo_step(positions, d0, box_size, alpha, rng)
            if accepted:
                positions = new_positions
                accepted_moves += 1
        
        # After equilibration, start sampling
        if cycle >= n_equilibration_cycles:
            sampled_positions.append(positions.copy())

    acceptance_rate = accepted_moves / total_moves if total_moves > 0 else 0

    return positions, acceptance_rate, sampled_positions

if __name__ == "__main__":
    # Example usage
    N_particles = 100
    box_size = 1.0
    
    # Example: target density A/A0 = 1.5, where A is the area of the box and A0 is the area of the particles.
    # A/A0 = 1 / (N * pi * (d0/2)^2) = 1 / (N * pi * d0^2 / 4) = 4 / (N * pi * d0^2)
    # d0^2 = 4 / (N * pi * (A/A0))
    # d0 = sqrt(4 / (N * pi * (A/A0))) = 2 / sqrt(N * pi * (A/A0))
    # Let's target a reasonable density, e.g., A/A0 = 2.0 (box area is 2x particle area)
    area_ratio = 2.0
    d0_diameter = 2 / np.sqrt(N_particles * np.pi * area_ratio)
    
    alpha_step_size = 0.05 * d0_diameter # A fraction of the particle diameter
    n_total_cycles = 100
    n_equilib_cycles = 20
    random_seed = 42

    print(f"Running simulation with N={N_particles}, d0={d0_diameter:.4f}, alpha={alpha_step_size:.4f}, cycles={n_total_cycles}")

    final_pos, acc_rate, samples = run_simulation(
        N_particles, d0_diameter, box_size, alpha_step_size, 
        n_total_cycles, n_equilib_cycles, random_seed
    )

    print(f"Final acceptance rate: {acc_rate:.2f}")
    print(f"Number of sampled configurations: {len(samples)}")

    # Basic check for overlaps in final configuration (for demonstration)
    overlaps_found = False
    for i in range(N_particles):
        for j in range(i + 1, N_particles):
            dist = calculate_distance(final_pos[i], final_pos[j], box_size)
            if dist < d0_diameter:
                overlaps_found = True
                print(f"Overlap found between particle {i} and {j} with distance {dist:.4f} < d0={d0_diameter:.4f}")
                break
        if overlaps_found:
            break
    
    if not overlaps_found:
        print("No overlaps found in the final configuration (within the check's scope).")
    else:
        print("Overlaps found in the final configuration.")

    # Another test: verify periodic boundary conditions for a single particle
    p_test = np.array([0.9, 0.9])
    p_moved = p_test + np.array([0.2, 0.2]) # Should wrap around to [0.1, 0.1]
    p_moved_wrapped = p_moved % box_size
    print(f"Test periodic boundary: original {p_test}, moved {p_moved}, wrapped {p_moved_wrapped}")
    assert np.allclose(p_moved_wrapped, np.array([0.1, 0.1]))
    print("Periodic boundary condition test passed.")

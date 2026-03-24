
import numpy as np

def initialize_particles(N, density_ratio, seed=None):
    """
    Initializes N particles in a square lattice configuration within a 1x1 box.
    Calculates particle diameter d0 based on N and desired density ratio.

    Args:
        N (int): Number of particles.
        density_ratio (float): A/A0, the ratio of box area to total particle area.
        seed (int, optional): Random seed for reproducibility. Defaults to None.

    Returns:
        tuple: (positions (np.ndarray), d0 (float))
    """
    if seed is not None:
        # The seed is for the Monte Carlo process, not for initial particle placement,
        # as initial placement is deterministic (lattice).
        # np.random.seed(seed) will be used by the simulation later for moves.
        pass # Keep this for future use by the MC algorithm

    # Box size is 1x1
    L = 1.0

    # Calculate d0 based on density_ratio
    # A/A0 = L*L / (N * pi * (d0/2)^2) = 4 / (N * pi * d0^2)
    # d0^2 = 4 / (N * pi * density_ratio)
    d0 = np.sqrt(4 / (N * np.pi * density_ratio))

    # Place particles in a square lattice
    n_rows = int(np.ceil(np.sqrt(N)))
    n_cols = int(np.ceil(N / n_rows))

    # Calculate spacing to fit n_cols particles across L
    spacing = L / n_cols

    positions = []
    current_particle_count = 0
    for i in range(n_rows):
        for j in range(n_cols):
            if current_particle_count < N:
                x = j * spacing + spacing / 2
                y = i * spacing + spacing / 2
                positions.append([x, y])
                current_particle_count += 1
            else:
                break
        if current_particle_count == N:
            break

    positions = np.array(positions)

    # Check for initial overlaps (should not happen with this lattice placement if d0 <= spacing)
    # This is a basic check and will be refined with the full overlap detection later
    min_dist_lattice = spacing
    if d0 > min_dist_lattice:
        print(f"Warning: d0 ({d0:.4f}) is greater than lattice spacing ({min_dist_lattice:.4f}). Initial overlaps possible.")
        # This situation implies that the requested density_ratio is too high for the initial lattice.
        # We might need a different initial configuration for very high densities.
        # For now, let's assume valid density_ratio that results in d0 <= spacing.


    return positions, d0


# --- Helper function for periodic boundary conditions and distance calculation ---
def wrap_coordinates(pos, L=1.0):
    """
    Applies periodic boundary conditions to particle coordinates.
    """
    return pos % L

def minimum_image_distance(p1, p2, L=1.0):
    """
    Calculates the minimum image distance between two particles in a periodic box.
    """
    dr = p1 - p2
    dr = dr - L * np.round(dr / L)
    return np.sqrt(np.sum(dr**2))

def check_overlap(positions, d0, L=1.0):
    """
    Checks for overlaps among all particles using minimum image convention.
    Returns True if any overlap is found, False otherwise.
    """
    N = len(positions)
    d0_sq = d0**2
    for i in range(N):
        for j in range(i + 1, N):
            dist_sq = np.sum((positions[i] - positions[j] - L * np.round((positions[i] - positions[j]) / L))**2)
            if dist_sq < d0_sq:
                return True
    return False


if __name__ == "__main__":
    # Example usage:
    N = 100
    density_ratio = 2.0  # Example A/A0
    seed = 42

    positions, d0 = initialize_particles(N, density_ratio, seed)

    print(f"Initialized {N} particles with d0 = {d0:.4f}")
    print("First 5 particle positions:")
    print(positions[:5])
    print(f"Min x: {np.min(positions[:,0]):.4f}, Max x: {np.max(positions[:,0]):.4f}")
    print(f"Min y: {np.min(positions[:,0]):.4f}, Max y: {np.max(positions[:,0]):.4f}")

    # Check for overlaps using the proper check_overlap function
    overlaps = check_overlap(positions, d0)
    print(f"Initial overlaps detected (proper check): {overlaps}")

    # Check reproducibility for initial d0
    positions_2, d0_2 = initialize_particles(N, density_ratio, seed)
    assert np.allclose(positions, positions_2) and np.isclose(d0, d0_2)
    print("Reproducibility check passed (d0 and initial positions are deterministic).")

    # Removed the assert for different seeds for positions, as initial positions are deterministic.

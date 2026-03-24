# Monte Carlo Simulation Implementation

def run_simulation(N, d0, box_size, alpha, n_cycles, n_equilib_cycles, seed=None):
    import numpy as np
    rng = np.random.default_rng(seed)

    # Initialize lattice with spacing avoiding overlaps
    positions = initialize_lattice(N, box_size, d0, seed)

    accepted_moves = 0
    total_moves = 0
    sampled_positions = []

    for cycle in range(n_cycles):
        for _ in range(N):  # One attempt per particle per cycle
            total_moves += 1
            new_positions, accepted = monte_carlo_step(
                positions, d0, box_size, alpha, rng
            )
            if accepted:
                positions = new_positions
                accepted_moves += 1

        if cycle >= n_equilib_cycles:
            sampled_positions.append(positions.copy())

    acceptance_rate = accepted_moves / total_moves if total_moves > 0 else 0
    return positions, acceptance_rate, sampled_positions
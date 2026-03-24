"""
Improved Monte Carlo Simulation for 2D Hard-Sphere Equation of State
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import time
from pathlib import Path

class HardSphereMC:
    """
    2D Hard-sphere Monte Carlo simulation with periodic boundary conditions
    """
    
    def __init__(self, N=100, box_size=1.0, d0=0.1, alpha=0.05, seed=None):
        """
        Initialize simulation parameters
        
        Args:
            N: Number of particles
            box_size: Box size (normalized to 1)
            d0: Particle diameter
            alpha: Maximum displacement step
            seed: Random seed for reproducibility
        """
        self.N = N
        self.box_size = box_size
        self.d0 = d0
        self.alpha = alpha
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Derived parameters
        self.A = box_size**2  # Area
        self.A0 = N * np.pi * (d0/2)**2  # Close-packed area
        self.density_ratio = self.A / self.A0  # A/A0
        self.rho = N / self.A  # Number density
        
        # Initialize particle positions on square lattice
        self.positions = self._initialize_lattice()
        
        # Statistics
        self.acceptance_count = 0
        self.total_moves = 0
        self.cycle_count = 0
        
    def _initialize_lattice(self):
        """Initialize particles on a square lattice"""
        n_side = int(np.ceil(np.sqrt(self.N)))
        spacing = self.box_size / n_side
        
        positions = np.zeros((self.N, 2))
        for i in range(self.N):
            row = i // n_side
            col = i % n_side
            positions[i, 0] = (col + 0.5) * spacing
            positions[i, 1] = (row + 0.5) * spacing
            
        return positions
    
    def _minimum_image_distance(self, pos1, pos2):
        """Compute minimum image distance between two positions"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        
        # Apply periodic boundary conditions
        dx -= self.box_size * np.round(dx / self.box_size)
        dy -= self.box_size * np.round(dy / self.box_size)
        
        return np.sqrt(dx**2 + dy**2)
    
    def _check_overlap(self, proposed_pos, particle_idx):
        """Check if proposed position overlaps with any other particle"""
        for j in range(self.N):
            if j == particle_idx:
                continue
                
            distance = self._minimum_image_distance(proposed_pos, self.positions[j])
            
            if distance < self.d0:
                return True  # Overlap detected
                
        return False  # No overlap
    
    def _propose_move(self, particle_idx):
        """Propose a random displacement for a particle"""
        # Random displacement within [-alpha, alpha]
        dx = np.random.uniform(-self.alpha, self.alpha)
        dy = np.random.uniform(-self.alpha, self.alpha)
        
        # New proposed position
        new_x = self.positions[particle_idx, 0] + dx
        new_y = self.positions[particle_idx, 1] + dy
        
        # Apply periodic boundary conditions
        new_x = new_x % self.box_size
        new_y = new_y % self.box_size
        
        return np.array([new_x, new_y])
    
    def _single_particle_move(self, particle_idx):
        """Attempt to move a single particle"""
        self.total_moves += 1
        
        # Propose new position
        proposed_pos = self._propose_move(particle_idx)
        
        # Check for overlap
        if not self._check_overlap(proposed_pos, particle_idx):
            # Accept move
            self.positions[particle_idx] = proposed_pos
            self.acceptance_count += 1
            return True
        else:
            # Reject move
            return False
    
    def run_cycle(self):
        """Run one complete MC cycle (attempt to move all particles)"""
        for i in range(self.N):
            self._single_particle_move(i)
        self.cycle_count += 1
    
    def get_acceptance_rate(self):
        """Get current acceptance rate"""
        if self.total_moves == 0:
            return 0.0
        return self.acceptance_count / self.total_moves
    
    def compute_rdf(self, max_r=None, nbins=200):
        """Compute radial distribution function g(r)"""
        if max_r is None:
            max_r = self.box_size / 2
        
        dr = max_r / nbins
        bins = np.zeros(nbins)
        bin_centers = np.arange(nbins) * dr + dr/2
        
        # Count pair distances
        for i in range(self.N):
            for j in range(i+1, self.N):
                distance = self._minimum_image_distance(self.positions[i], self.positions[j])
                if distance < max_r:
                    bin_idx = int(distance / dr)
                    if bin_idx < nbins:
                        bins[bin_idx] += 2  # Count both i-j and j-i
        
        # Normalize
        rho = self.N / self.A
        for i in range(nbins):
            r_inner = i * dr
            r_outer = (i+1) * dr
            shell_volume = np.pi * (r_outer**2 - r_inner**2)
            ideal_count = rho * shell_volume * self.N
            if ideal_count > 0:
                bins[i] /= ideal_count
        
        return bin_centers, bins
    
    def compute_contact_density(self):
        """Compute contact density n̄ from RDF"""
        bin_centers, g_r = self.compute_rdf()
        
        # Find g(r) at contact distance by interpolating around d0
        contact_idx = np.argmin(np.abs(bin_centers - self.d0))
        
        # Use linear interpolation to get better estimate at exactly d0
        if contact_idx > 0 and contact_idx < len(bin_centers) - 1:
            # Interpolate between neighboring bins
            r1, r2 = bin_centers[contact_idx-1], bin_centers[contact_idx+1]
            g1, g2 = g_r[contact_idx-1], g_r[contact_idx+1]
            
            if r2 != r1:
                g_contact = g1 + (g2 - g1) * (self.d0 - r1) / (r2 - r1)
            else:
                g_contact = g_r[contact_idx]
        else:
            g_contact = g_r[contact_idx]
        
        # Contact density
        n_bar = self.rho * g_contact
        return n_bar
    
    def compute_pressure(self):
        """Compute pressure using equation of state"""
        n_bar = self.compute_contact_density()
        
        # Reduced pressure
        reduced_pressure = 1 + (np.pi * self.d0**2 * n_bar) / 2
        
        return reduced_pressure
    
    def run_equilibration(self, n_cycles=10):
        """Run equilibration cycles without recording data"""
        for _ in range(n_cycles):
            self.run_cycle()
    
    def run_production(self, n_cycles=50, record_every=1):
        """Run production cycles and record data"""
        pressures = []
        acceptance_rates = []
        
        for i in range(n_cycles):
            self.run_cycle()
            
            if (i+1) % record_every == 0:
                pressure = self.compute_pressure()
                pressures.append(pressure)
                acceptance_rates.append(self.get_acceptance_rate())
        
        return {
            'pressures': np.array(pressures),
            'acceptance_rates': np.array(acceptance_rates),
            'mean_pressure': np.mean(pressures),
            'std_pressure': np.std(pressures)
        }


def run_parameter_sweep(N=100, n_densities=10, production_cycles=50, output_dir='results'):
    """Run parameter sweep over different densities"""
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    results = []
    
    # Density range from low to high
    density_ratios = np.logspace(np.log10(1.2), np.log10(4.0), n_densities)
    
    for i, density_ratio in enumerate(density_ratios):
        print(f"Running simulation {i+1}/{n_densities} with A/A0 = {density_ratio:.2f}")
        
        # Compute d0 from density ratio
        A = 1.0  # Box size = 1
        A0 = A / density_ratio
        d0 = np.sqrt(4 * A0 / (N * np.pi))
        
        # Adjust alpha based on density (smaller steps for higher density)
        alpha = min(0.05, 0.1 * d0)
        
        # Create simulation
        mc = HardSphereMC(N=N, box_size=1.0, d0=d0, alpha=alpha, seed=42)
        
        # Equilibration
        mc.run_equilibration(15)
        
        # Production
        data = mc.run_production(production_cycles, record_every=1)
        
        result = {
            'density_ratio': density_ratio,
            'd0': d0,
            'mean_pressure': data['mean_pressure'],
            'std_pressure': data['std_pressure'],
            'final_acceptance_rate': mc.get_acceptance_rate(),
            'alpha': alpha
        }
        results.append(result)
        
        print(f"  Mean pressure: {data['mean_pressure']:.4f} ± {data['std_pressure']:.4f}")
        print(f"  Acceptance rate: {mc.get_acceptance_rate():.3f}")
        print(f"  Alpha: {alpha:.4f}")
    
    # Save results
    results_file = Path(output_dir) / 'parameter_sweep_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


def create_plots(results, output_dir='results'):
    """Create diagnostic plots"""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    # Extract data
    density_ratios = [r['density_ratio'] for r in results]
    pressures = [r['mean_pressure'] for r in results]
    std_pressures = [r['std_pressure'] for r in results]
    acceptance_rates = [r['final_acceptance_rate'] for r in results]
    
    # Plot 1: Equation of state
    plt.figure(figsize=(10, 6))
    plt.errorbar(density_ratios, pressures, yerr=std_pressures, fmt='o-', label='Simulation', capsize=3)
    
    # Theoretical curves
    rho = 100 / (1.0**2)  # Number density
    
    # Low density: virial expansion (second virial coefficient)
    # B2 = π * d0^2 / 2 for 2D hard spheres
    # But we need to compute this for each density
    
    # High density: free volume theory
    # P = 1 / (1 - η) where η is packing fraction
    # η = N * π * (d0/2)^2 / A = A0 / A = 1 / (A/A0)
    
    # Create theoretical curves
    theory_ratios = np.linspace(min(density_ratios), max(density_ratios), 100)
    
    # Virial expansion (low density)
    virial_pressures = []
    for ratio in theory_ratios:
        if ratio >= 3.0:  # Low density regime
            eta = 1.0 / ratio  # Packing fraction
            d0 = np.sqrt(4 * eta / (100 * np.pi))
            b2 = np.pi * d0**2 / 2  # Second virial coefficient
            virial_p = 1 + b2 * (100 / 1.0**2)
            virial_pressures.append(virial_p)
        else:
            virial_pressures.append(np.nan)
    
    # Free volume theory (high density)
    fv_pressures = []
    for ratio in theory_ratios:
        if ratio <= 1.5:  # High density regime
            eta = 1.0 / ratio  # Packing fraction
            fv_p = 1 / (1 - eta)
            fv_pressures.append(fv_p)
        else:
            fv_pressures.append(np.nan)
    
    plt.plot(theory_ratios, virial_pressures, '--', label='Virial (low density)', alpha=0.7, linewidth=2)
    plt.plot(theory_ratios, fv_pressures, '--', label='Free volume (high density)', alpha=0.7, linewidth=2)
    
    plt.xlabel('A/A₀ (Density ratio)')
    plt.ylabel('PA/NkT (Reduced pressure)')
    plt.title('Equation of State - 2D Hard Spheres')
    plt.xscale('log')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(Path(output_dir) / 'eos_curve.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Acceptance rate vs density
    plt.figure(figsize=(10, 6))
    plt.plot(density_ratios, acceptance_rates, 'o-', linewidth=2, markersize=8)
    plt.xlabel('A/A₀ (Density ratio)')
    plt.ylabel('Acceptance rate')
    plt.title('Acceptance Rate vs Density')
    plt.xscale('log')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(Path(output_dir) / 'acceptance_rate.png', dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    print("Starting improved Monte Carlo simulation for 2D hard spheres...")
    start_time = time.time()
    
    # Run parameter sweep
    results = run_parameter_sweep(N=100, n_densities=8, production_cycles=100)
    
    # Create plots
    create_plots(results)
    
    # Print summary
    print(f"\nSimulation completed in {time.time() - start_time:.1f} seconds")
    print(f"Results saved to results/ directory")
    
    # Print key findings
    print("\nKey findings:")
    for i, result in enumerate(results):
        print(f"A/A₀ = {result['density_ratio']:.2f}: PA/NkT = {result['mean_pressure']:.3f} ± {result['std_pressure']:.3f}")
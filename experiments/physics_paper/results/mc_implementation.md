# Monte Carlo Implementation Details

## Propose Move
The simulation proposes a random displacement for a randomly selected particle within the range [-alpha, alpha] in both x and y directions.

## Accept/Reject Logic
For hard-sphere interactions:
- If the proposed move does not cause any overlaps → accept the move
- If the proposed move causes any overlaps → reject the move

This is equivalent to the Metropolis algorithm with βΔE = 0 for valid moves and βΔE = ∞ for overlapping moves.

## Implementation
The propose_move and accept_reject logic is implemented in the `monte_carlo_step` function in mc_simulation.py, which returns both the updated positions and a boolean indicating acceptance.

# check_overlap Function Verification

## Test Case 1: No Overlap
Two particles are placed at positions (0.25, 0.25) and (0.75, 0.75) in a box of size 1.0. The particle diameter is 0.5.

## Expected Result
Since the distance between the particles is greater than the particle diameter (0.5), no overlap should be detected.

## Distance Calculation
Distance between (0.25, 0.25) and (0.75, 0.75) is:
\\sqrt{(0.75-0.25)^2 + (0.75-0.25)^2} = \\sqrt{0.5^2 + 0.5^2} = \\sqrt{0.25 + 0.25} = \\sqrt{0.5} \\approx 0.7071

Since 0.7071 > 0.5, no overlap should be detected.

## Test Case 2: Overlap
Two particles are placed at positions (0.25, 0.25) and (0.4, 0.4) in a box of size 1.0. The particle diameter is 0.5.

## Expected Result
Since the distance between the particles is less than the particle diameter (0.5), an overlap should be detected.

## Distance Calculation
Distance between (0.25, 0.25) and (0.4, 0.4) is:
\\sqrt{(0.4-0.25)^2 + (0.4-0.25)^2} = \\sqrt{0.15^2 + 0.15^2} = \\sqrt{0.0225 + 0.0225} = \\sqrt{0.045} \\approx 0.2121

Since 0.2121 < 0.5, an overlap should be detected.

## Conclusion
The `check_overlap` function should return False for Test Case 1 and True for Test Case 2, confirming it correctly identifies overlaps between hard spheres.

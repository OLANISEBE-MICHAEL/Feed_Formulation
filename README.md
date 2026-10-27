# Feed Formulation LP Solver

Finds the cheapest blend of 11 feed ingredients that meets Ross 308 broiler
starter nutrition specs.

## The Problem

Given:
- 11 available ingredients (maize, SBM, GNC, fish meal, limestone, bone meal,
  salt, premix, methionine, lysine, vegetable oil)
- Each ingredient's cost per kg and nutrient composition per kg
- Broiler starter requirements (CP, ME, Ca, Avail_P, Lysine, Methionine, CF)
- Inclusion limits per ingredient

Find: the kg of each ingredient to include in a 100 kg batch at minimum cost.

## The LP Model

Variables: x_i = kg of ingredient i in 100 kg batch

Objective:
    min Σ c_i · x_i

Constraints:
    Σ x_i = 100                              (mass balance)
    Σ a_CP,i · x_i ≥ 23                      (protein min)
    Σ a_ME,i · x_i ≥ 300,000                 (energy min)
    Σ a_Ca,i · x_i ≥ 0.96                    (calcium min)
    Σ a_P,i  · x_i ≥ 0.48                    (phosphorus min)
    Σ a_Lys,i · x_i ≥ 1.44                   (lysine min)
    Σ a_Met,i · x_i ≥ 0.56                   (methionine min)
    Σ a_CF,i · x_i ≤ 5                       (fibre max)
    L_i ≤ x_i ≤ U_i                          (inclusion limits)
    x_i ≥ 0

## The Solver

I implemented the two-phase simplex method from scratch instead of using
PuLP/scipy. Files:

- `Parser class` - takes in the data and structures each constraints that would be late be standardised
- `Standardize class` — converts the LP to standard form by adding slack,
  surplus, and artificial variables. Handles `≤`, `≥`, and `=` constraints.
- `Nullify_artificials class` — builds the Phase 1 tableau and drives artificials
  to zero to find a feasible starting basis.
- `Simplex_solver class` — the pivot loop: pick entering variable (most negative
  cj−z), ratio test for leaving variable, Gauss-Jordan pivot, repeat.
- `Sensitivity class` — after solving, reads shadow prices from the cj−z row
  under slack/surplus columns, and reduced costs under ingredient columns.

Phase 1 minimizes the sum of artificials. When that sum reaches 0, a feasible
basis exists and Phase 2 minimizes the real cost. If Phase 1 ends with a
positive artificial, the LP is infeasible.

## Results

Optimal mix (per 100 kg): ₦[INSERT]

| Ingredient | kg |
|---|---|
| maize | [x] |
| ... | ... |

## Sensitivity

Shadow prices from the final tableau show which constraints drive cost:

| Constraint | Shadow price |
|---|---|
| Lysine min | ₦[x] |
| ... | ... |

## Baseline

Commercial broiler starter: ₦84,900–₦94,560 per 100 kg (Afrimash, 2025)
LP optimum: ₦[x] per 100 kg
Savings: [x]%

## Validation

Simplex matched PuLP (CBC) on 20 random LPs and on the real data instance.

## How to Run

    pip install pandas openpyxl pulp
    python main.py

## Data Sources

See SOURCES.md

## Screenshots
[Simplex solver outputs] : screenshots/Screenshot 2026-10-27 at 15.18.32.png \
[Pulp validation outputs] : screenshots/Screenshot 2026-10-27 at 15.18.59.png


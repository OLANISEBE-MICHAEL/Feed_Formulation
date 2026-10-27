# Data Sources

## Nutritional Requirements

Broiler starter requirements (per kg of feed) used in `requirements.xlsx`:

| Nutrient | Min | Max |
|---|---|---|
| CP | 0.23 | — |
| ME | 3000 | — |
| Ca | 0.0096 | — |
| Avail_P | 0.0048 | — |
| Lysine | 0.0144 | — |
| Methionine | 0.0056 | — |
| CF | — | 0.05 |

**Source:** Ross 308 Broiler Nutrition Specifications (Aviagen, 2014), Starter
column (0–10 days). Crude fibre max from NRC (2012) broiler starter spec.

Reference: https://en.aviagen.com/ross-308/

## Ingredient Composition

Composition data used in `composition.xlsx` (values per kg of ingredient).
Approximate values compiled from NRC (2012) Nutrient Requirements of Poultry,
Table A-4, with cross-verification from Feedipedia.org.

| Ingredient | CP | ME (kcal/kg) | Ca | Avail_P | Lysine | Methionine | CF |
|---|---|---|---|---|---|---|---|
| maize | 0.085 | 3350 | 0.0002 | 0.001 | 0.0024 | 0.0018 | 0.02 |
| soybean_meal | 0.44 | 2230 | 0.003 | 0.002 | 0.028 | 0.006 | 0.07 |
| groundnut_cake | 0.40 | 2450 | 0.002 | 0.001 | 0.013 | 0.004 | 0.12 |
| fish_meal | 0.60 | 2900 | 0.05 | 0.025 | 0.045 | 0.017 | 0.005 |
| limestone | 0 | 0 | 0.38 | 0 | 0 | 0 | 0 |
| bone_meal | 0 | 0 | 0.30 | 0.15 | 0 | 0 | 0 |
| salt | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| premix | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| methionine | 0 | 0 | 0 | 0 | 0 | 0.99 | 0 |
| lysine | 0 | 0 | 0 | 0 | 0.78 | 0 | 0 |
| vegetable_oil | 0 | 8800 | 0 | 0 | 0 | 0 | 0 |

## Ingredient Prices

Nigerian market prices (per kg), October 2026. Values used in
`ingredients.xlsx`:

| Ingredient | ₦/kg | Min kg | Max kg |
|---|---|---|---|
| maize | 500 | 0 | 60 |
| soybean_meal | 900 | 0 | 40 |
| groundnut_cake | 650 | 0 | 25 |
| fish_meal | 1500 | 0 | 5 |
| limestone | 200 | 1 | 3 |
| bone_meal | 400 | 0 | 2 |
| salt | 150 | 0 | 0.5 |
| premix | 3000 | 0.5 | 0.5 |
| methionine | 4500 | 0 | 0.3 |
| lysine | 3000 | 0 | 0.3 |
| vegetable_oil | 2500 | 0 | 5 |

Prices are approximate market rates from Nigerian agri suppliers (Afrimash,
HTS Farms). Inclusion limits (min/max) follow practical broiler starter
formulation constraints — palatability, anti-nutritional factors, and
nutritional balance.

## Baseline Comparison

Commercial broiler starter prices in Nigeria (2025 market rates):

- **New Hope Broiler Starter** (25 kg bag): ₦21,225 – ₦23,640
  → **₦84,900 – ₦94,560 per 100 kg**
- **TopFeeds Starter** (25 kg bag): ₦23,654 – ₦24,650
  → **₦94,616 – ₦98,600 per 100 kg**

Source: Afrimash.com and HTS Farms product listings, accessed October 2026.

## Validation Reference

PuLP 2.x with CBC solver used as an independent reference implementation.
Random LP instances generated with fixed seeds; objective values matched
between the custom two-phase simplex solver and PuLP within 1e-4 relative
tolerance.
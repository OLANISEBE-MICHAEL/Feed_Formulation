import pandas as pd
import pulp

ing = pd.read_excel("/Users/eniola/Desktop/projects_n_stuff/feed_formulation/test_data/ingredients.xlsx")
comp = pd.read_excel("/Users/eniola/Desktop/projects_n_stuff/feed_formulation/test_data/composition.xlsx")
req = pd.read_excel("/Users/eniola/Desktop/projects_n_stuff/feed_formulation/test_data/requirements.xlsx")

ingredients = ing["name"].tolist()
nutrients = req["nutrient"].tolist()
batch = 100

prob = pulp.LpProblem("feed_real", pulp.LpMinimize)
x = {i: pulp.LpVariable(f"x_{i}", lowBound=0) for i in ingredients}

# objective
prob += pulp.lpSum(ing.set_index("name").loc[i, "cost_per_kg"] * x[i] for i in ingredients)

# mass balance
prob += pulp.lpSum(x[i] for i in ingredients) == batch

# nutrient constraints
for nut in nutrients:
    req_row = req[req["nutrient"] == nut].iloc[0]
    coeffs = {}
    for _, r in comp[comp["nutrient"] == nut].iterrows():
        coeffs[r["ingredient"].strip()] = r["amount_per_kg"]
    expr = pulp.lpSum(coeffs.get(i, 0) * x[i] for i in ingredients)
    if pd.notna(req_row["min"]):
        prob += expr >= req_row["min"] * batch
    if pd.notna(req_row["max"]):
        prob += expr <= req_row["max"] * batch

# inclusion limits
for _, row in ing.iterrows():
    if pd.notna(row["min_kg"]) and row["min_kg"] > 0:
        prob += x[row["name"]] >= row["min_kg"]
    if pd.notna(row["max_kg"]):
        prob += x[row["name"]] <= row["max_kg"]

prob.solve(pulp.PULP_CBC_CMD(msg=0))

print(f"Status: {pulp.LpStatus[prob.status]}")
print(f"Objective: ₦{pulp.value(prob.objective):.4f}")
print("Mix:")
for i in ingredients:
    print(f"  {i}: {x[i].varValue:.4f} kg")
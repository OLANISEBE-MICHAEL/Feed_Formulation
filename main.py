import pandas as pd
import math

class ParseData:
    # gets in the paths to the data we are going to be using and then parses it in the format that is acceptable for the algorithm
    def __init__(self, data_paths : dict, max_balance : float):
        self.data_paths = data_paths
        self.max_balance = max_balance
        self.ingr_df = self.get_df("ingredients")
        self.comp_df = self.get_df("composition")
        self.req_df = self.get_df("requirements")
        self.variables = self.get_variable()
        self.costs = self.get_cost()
        self.objective_function = self.get_objective_function()
        self.inclusion_limits = self.get_inclusion_limits()
        self.nutritional_requirements = self.get_requirements()



    def get_df(self, name) -> pd.DataFrame:
        # reads the ms excel paths and then returns a data fram
        return pd.read_excel(self.data_paths[name], engine='openpyxl')

    def parse_options(self, value):
        """return float or None if there is value missing or not"""
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        return value.__float__()

    def get_variable(self) -> list:
        # gets all the ingredient form the ingredient excel file
        return self.ingr_df["name"].to_list()

    def get_cost(self) -> list:
        # gets each ingredient cost
        return self.ingr_df["cost_per_kg"].to_list()

    def get_inclusion_limits(self) -> dict:
        # get's the inclusion limits of all the ingredients, this a constraint that needs to be considered by the algorithm
        inclu_dict = {}
        min_kg, max_kg = self.ingr_df["min_kg"].to_list(), self.ingr_df["max_kg"].to_list()
        for i in range(len(min_kg)):
            inclu_dict[self.variables[i]] = {
                "min_kg": self.parse_options(min_kg[i]), "max_kg": self.parse_options(max_kg[i])
            }
        return inclu_dict

    def get_objective_function(self) -> dict:
        # this is the function that contains all the decision variables, we are trying to minimize the cost
        obj_dict = {}
        for i in range(len(self.variables)):
            obj_dict[self.variables[i]] = self.costs[i]
        return obj_dict

    def get_requirements(self) -> dict:
        # gets all the requirements from the microsoft-excel file, this forms the other constraint for the nutrients that would be inside the feed
        constraint_dict = {}
        nutrient_needed = self.req_df["nutrient"].to_list()
        for nutrient in nutrient_needed:
            # we have to get all the ingredients, amounts needed for each specific nutrient and also the min or max requirements for that specific nutrient. this forms the constraint
            constraint_dict[nutrient] = {
                "variable": self.comp_df[self.comp_df["nutrient"] == nutrient]["ingredient"].to_list(),
                "amount_per_kg": self.comp_df[self.comp_df["nutrient"] == nutrient]["amount_per_kg"].to_list(),
                "min_requirement": self.parse_options(self.req_df[self.req_df["nutrient"] == nutrient]["min"].iat[0]),
                "max_requirement": self.parse_options(self.req_df[self.req_df["nutrient"] == nutrient]["max"].iat[0]),
            }
        return constraint_dict


class Standardize:
    # this deals with taking all the gathered data from the excel file and turning it into equations we can feed into the algorithm

    def __init__(self, parsed_object : ParseData):
        self.parsed_object = parsed_object
        self.nutri_req = self.parsed_object.nutritional_requirements
        self.additional_variable_counter = {
            "slack": 1,
            "surplus": 1,
            "artificial": 2
        }
        self.max_balance_constraint = self.get_max_balance_constraint()
        self.nutritional_constraints = self.get_nutritional_constraints()
        self.inclusion_limit_constraints = self.get_inclusion_limit_constraints()

    def get_additional_variables(self, inequality_symbol) -> list:
        if inequality_symbol == "≥":
          return [("surplus", -1), ("artificial", 1)]
        elif inequality_symbol == "≤":
            return [("slack", 1)]
        elif inequality_symbol == "=":
            return [("artificial", 1)]
        return []

    def derive_nutritional_equation(self, constraint_dict):
        # deriving the equation involves adding whether a slack, surplus or artificial variable based on the inequality symbol
        for nutrient in constraint_dict:
            inequality_symbol = constraint_dict[nutrient]["inequality_symbol"]
            additional_variables = self.get_additional_variables(inequality_symbol)
            for var in additional_variables:
                constraint_dict[nutrient]["left_hand_side"][f"{var[0]}_{self.additional_variable_counter[var[0]]}"] = var[1]
                self.additional_variable_counter[var[0]] += 1

    def derive_inclusion_limit_equation(self, constraint_dict):
        # deriving the equation involves adding whether a slack, surplus or artificial variable based on the inequality symbol
        for equation in constraint_dict:
            inequality_symbol =  constraint_dict[equation]["inequality_symbol"]
            additional_variables = self.get_additional_variables(inequality_symbol)
            for var in additional_variables:
                constraint_dict[equation]["left_hand_side"][f"{var[0]}_{self.additional_variable_counter[var[0]]}"] = var[1]
                self.additional_variable_counter[var[0]] += 1

    def derive_max_balance_equation(self, constraint_dict):
        # deriving the equation involves adding whether a slack, surplus or artificial variable based on the inequality symbol
        inequality_symbol = constraint_dict["equation"]["inequality_symbol"]
        additional_variables = self.get_additional_variables(inequality_symbol)
        constraint_dict["equation"]["left_hand_side"][f"{additional_variables[0][0]}_1"] = additional_variables[0][1]


    def display_equations(self):
        all_equations = ""
        # for max balance constraints
        left_hand_side = ""
        for key, value in self.max_balance_constraint["equation"]["left_hand_side"].items(): left_hand_side += f"{value}({key}) + "
        right_hand_side = self.max_balance_constraint["equation"]["right_hand_side"]
        if left_hand_side.endswith("+ "):
            left_hand_side = left_hand_side[:-2]
        all_equations += f"{left_hand_side} = {right_hand_side}\n"

        # for all nutritional constraints
        for nutrient in self.nutritional_constraints:
            left_hand_side = ""
            for key, value in self.nutritional_constraints[nutrient]["left_hand_side"].items(): left_hand_side += f"{value}({key}) + "
            right_hand_side = self.nutritional_constraints[nutrient]["right_hand_side"]
            if left_hand_side.endswith("+ "):
                left_hand_side = left_hand_side[:-2]
            all_equations += f"{left_hand_side} = {right_hand_side}\n"

        # for all inclusion limit constraints
        for equation in self.inclusion_limit_constraints:
            left_hand_side = ""
            for key, value in self.inclusion_limit_constraints[equation]["left_hand_side"].items() : left_hand_side += f"{value}({key}) + "
            right_hand_side = self.inclusion_limit_constraints[equation]["right_hand_side"]
            if left_hand_side.endswith("+ "):
                left_hand_side = left_hand_side[:-2]
            all_equations += f"{left_hand_side} = {right_hand_side}\n"

        print(all_equations)

    def get_nutritional_constraints(self) -> dict:
        # getting the nutritional constraints from nutritional requirements
        constraint_dict = {}
        for nutrient in self.nutri_req:
            min_req = self.nutri_req[nutrient]["min_requirement"]
            max_req = self.nutri_req[nutrient]["max_requirement"]

            # building the left hand side variables and coefficients
            coefficients = {
                self.nutri_req[nutrient]["variable"][i] : self.nutri_req[nutrient]["amount_per_kg"][i]
                for i in range(len(self.nutri_req[nutrient]["variable"]))
                if self.nutri_req[nutrient]["amount_per_kg"][i] != 0.0
            }

            # skipping nutrient with no min and max requirement
            if min_req == 0.0 and max_req == 0.0:
                continue

            # there could be missing values for the min or max
            if (min_req == 0.0 or min_req is None) and (max_req == 0.0 or max_req is None):
                continue

            # generating minimum constraint if present
            if min_req is not None and min_req > 0.0:
                constraint_dict[f"{nutrient}_min"] = {
                    "left_hand_side" : coefficients,
                    "inequality_symbol" : "≥",
                    "right_hand_side" : min_req * self.parsed_object.max_balance,
                }

            # generating maximum constraint if present
            if max_req is not None and max_req > 0.0:
                constraint_dict[f"{nutrient}_max"] = {
                    "left_hand_side" : coefficients,
                    "inequality_symbol": "≤",
                    "right_hand_side" : max_req * self.parsed_object.max_balance,
                }
        self.derive_nutritional_equation(constraint_dict)
        return constraint_dict

    def get_inclusion_limit_constraints(self) -> dict:
        # get the constraint from the inclusion limit excel file
        inclusion_limit_dict = {}
        ingredient_w_range = []

        for index, ingredient in enumerate(self.parsed_object.inclusion_limits):
            min_kg , max_kg =  self.parsed_object.inclusion_limits[ingredient]["min_kg"], self.parsed_object.inclusion_limits[ingredient]["max_kg"]
            # this is to check that that particular ingredient does not have a range. (when you have an inclusion of min and max that is already a specified range)
            if not min_kg != 0 and max_kg != 0:
                inclusion_limit_dict[f"equation_{index + 1}"] = {
                    "left_hand_side": {
                        ingredient : 1,
                    },
                    "inequality_symbol": "≤" if min_kg == 0 else "≥",
                    "right_hand_side": max_kg if min_kg == 0 else min_kg
                }
            else:
                ingredient_w_range.append((ingredient, min_kg, max_kg))
        if inclusion_limit_dict:
            last_equation = int(list(inclusion_limit_dict.keys())[-1].split("_")[-1])
        else:
            last_equation = 0

        for ingredient_detail in ingredient_w_range:
            last_equation += 1
            inclusion_limit_dict[f"equation_{last_equation}"] = {
                "left_hand_side" : {
                    ingredient_detail[0] : 1,
                },
                "inequality_symbol" : "≥",
                "right_hand_side": ingredient_detail[1]
            }
            last_equation += 1
            inclusion_limit_dict[f"equation_{last_equation}"] = {
                "left_hand_side" : {
                    ingredient_detail[0] : 1,
                },
                "inequality_symbol" : "≤",
                "right_hand_side": ingredient_detail[2]

            }
        self.derive_inclusion_limit_equation(inclusion_limit_dict)
        return inclusion_limit_dict

    def get_max_balance_constraint(self) -> dict:
        max_balance_dict = {}
        max_balance_dict["equation"] = {
            "left_hand_side": {ingredient : 1 for ingredient in self.parsed_object.variables},
            "inequality_symbol": "=",
            "right_hand_side": self.parsed_object.max_balance
        }
        self.derive_max_balance_equation(max_balance_dict)
        return max_balance_dict

class NullifyArtificials:
    # this is the first running of the algorithm, it runs an iteration in an attempt to nullify all artificial variables. this determines whether the problem is feasible or not
    def __init__(self, standardize_object : Standardize):
        self.standardize_object = standardize_object
        self.all_equations = []
        self.get_all_equations()
        self.all_variables = set()
        self.basis_variables = {}
        self.get_basis_variables()
        self.cj_dict = self.get_cj_dict()
        self.get_basis_variables_coefficients()
        self.row_dict = self.get_row_dict()
        self.zj_dict = self.get_z_dict()
        self.cj_minus_z_dict = self.get_cj_minus_z_dict()

    def display_table(self):
        print(f"Variables | {self.all_variables}")
        print(f"CJ | {self.cj_dict}")
        for row in self.row_dict:
            print(f"{self.basis_variables[row]} | {row} | {self.row_dict[row]}")
        print(f"ZJ | {self.zj_dict}")
        print(f"CJ - Z | {self.cj_minus_z_dict}")
        print("\n")

    def organize_variables(self):
        # to make sure all cj values have a definite order
        auxiliary_variables = []
        for equation in self.all_equations:
            for key in equation[0]:
                if key not in self.standardize_object.parsed_object.variables:
                    auxiliary_variables.append(key)
        organized_variables = self.standardize_object.parsed_object.variables + auxiliary_variables
        self.all_variables = organized_variables # it should be the decision variables first followed by the auxilary variables, that is the order.

    def get_basis_variables(self):
        # the functions gets all the variables including the basis variables for each category of constraints
        self.get_max_balance_constraint_variables()
        self.get_nutritional_variables()
        self.get_inclusion_limit_variables()

    def get_all_equations(self):
        # this gets all the equations in order of max balance, nutritional and then inclusion limits
        self.get_max_balance_equation()
        self.get_nutritional_equation()
        self.get_inclusion_limit_equation()

    def get_basis_variables_coefficients(self):
        for variable in self.cj_dict:
            if variable in self.basis_variables:
                self.basis_variables[variable] = self.cj_dict[variable]

    def get_max_balance_constraint_variables(self):
        left_hand_side = self.standardize_object.max_balance_constraint["equation"]["left_hand_side"]
        max_balance_variables = list(left_hand_side.keys())
        self.all_variables.update(max_balance_variables)
        basis_variable = max_balance_variables[-1] # we know that other additional variables are the ones going to be the last in the equations
        self.basis_variables[basis_variable] = None

    def get_nutritional_variables(self):
        for nutrient in self.standardize_object.nutritional_constraints:
            left_hand_side = self.standardize_object.nutritional_constraints[nutrient]["left_hand_side"]
            nutritional_variables = list(left_hand_side.keys())
            self.all_variables.update(nutritional_variables)
            basis_variable = nutritional_variables[-1]
            self.basis_variables[basis_variable] = None

    def get_inclusion_limit_variables(self):
        for equations in self.standardize_object.inclusion_limit_constraints:
            left_hand_side = self.standardize_object.inclusion_limit_constraints[equations]["left_hand_side"]
            inclusion_limit_variables = list(left_hand_side.keys())
            self.all_variables.update(inclusion_limit_variables)
            basis_variable = inclusion_limit_variables[-1]
            self.basis_variables[basis_variable] = None

    def get_max_balance_equation(self):
        left_hand_side = self.standardize_object.max_balance_constraint["equation"]["left_hand_side"]
        right_hand_side = self.standardize_object.max_balance_constraint["equation"]["right_hand_side"]
        self.all_equations.append((left_hand_side, right_hand_side))

    def get_nutritional_equation(self):
        for nutrient in self.standardize_object.nutritional_constraints:
            left_hand_side = self.standardize_object.nutritional_constraints[nutrient]["left_hand_side"]
            right_hand_side = self.standardize_object.nutritional_constraints[nutrient]["right_hand_side"]
            self.all_equations.append((left_hand_side, right_hand_side))

    def get_inclusion_limit_equation(self):
        for equations in self.standardize_object.inclusion_limit_constraints:
            left_hand_side = self.standardize_object.inclusion_limit_constraints[equations]["left_hand_side"]
            right_hand_side = self.standardize_object.inclusion_limit_constraints[equations]["right_hand_side"]
            self.all_equations.append((left_hand_side, right_hand_side))

    def get_cj_dict(self) -> dict:
        # this is because the objective for the phase is to reduce the artificials to zero.
        self.organize_variables()
        cj_dict = {}
        for var in self.all_variables:
            if var.startswith("artificial"):
                cj_dict[var] = 1
            else:
                cj_dict[var] = 0
        return cj_dict

    def get_row_dict(self) -> dict:
        row_dict = {}
        for index, basis in enumerate(self.basis_variables):
            row_dict[basis] = {
                var : self.all_equations[index][0][var] if var in self.all_equations[index][0] else 0 for var in self.all_variables
            }
            row_dict[basis]["rhs"] = self.all_equations[index][1]
        return row_dict

    def get_z_dict(self) -> dict:
        # we are multiplying the coefficients of the basis variable with each variable's column
        z_dict = {}
        for variable in self.all_variables:
            sum_of_multiplication = 0
            for basis_var in self.row_dict:
                sum_of_multiplication += self.basis_variables[basis_var] * self.row_dict[basis_var][variable]

            z_dict[variable] = sum_of_multiplication
        return z_dict

    def get_cj_minus_z_dict(self) -> dict:
        cjz_dict = {}
        for key in self.cj_dict:
            cjz_dict[key] = self.cj_dict[key] - self.zj_dict[key]
        return cjz_dict


class SimplexSolver:

    def __init__(self, nullify_artificials : NullifyArtificials, debug=True):
        self.most_negative_number = 0
        self.most_negative_variable = None
        self.ratio_details = {}
        self.pivot_details = {}
        self.nullify_artificials = nullify_artificials
        self.debug = debug


    def get_pivot_details(self):
        # determining the pivot column from cj - z
        pivot_column = []

        self.most_negative_number = next(iter(self.nullify_artificials.cj_minus_z_dict.values()))
        self.most_negative_variable = next(iter(self.nullify_artificials.cj_minus_z_dict.keys()))
        for variable in self.nullify_artificials.cj_minus_z_dict:
            if self.nullify_artificials.cj_minus_z_dict[variable] < self.most_negative_number:
                self.most_negative_number = self.nullify_artificials.cj_minus_z_dict[variable]
                self.most_negative_variable = variable

        # determining the pivot row
        self.ratio_details = {"lowest_ratio" : (100000000000 * 40000000000), "pivot_row_var": None}
        for auxiliary_variable in self.nullify_artificials.row_dict:
            try:
                # divide each rhs with the corresponding value on the pivot column
                current_ratio = self.nullify_artificials.row_dict[auxiliary_variable]["rhs"] / self.nullify_artificials.row_dict[auxiliary_variable][self.most_negative_variable]
            except ZeroDivisionError:
                current_ratio = -1
            else:
                # keeps updating the lowest ratio till we get the actual lowest
                if 0 <= current_ratio < self.ratio_details["lowest_ratio"]:
                    self.ratio_details["lowest_ratio"] = current_ratio
                    self.ratio_details["pivot_row_var"] = auxiliary_variable
            pivot_column.append(self.nullify_artificials.row_dict[auxiliary_variable][self.most_negative_variable])
        pivot_row = list(self.nullify_artificials.row_dict[self.ratio_details["pivot_row_var"]].values())
        pivot_element = self.nullify_artificials.row_dict[self.ratio_details["pivot_row_var"]][self.most_negative_variable]

        self.pivot_details["pivot_column"] = pivot_column
        self.pivot_details["pivot_row"] = pivot_row
        self.pivot_details["pivot_element"] = pivot_element

        if self.debug:
            print(f"Pivot Column: {self.pivot_details["pivot_column"]}")
            print(f"Pivot Row: {self.pivot_details["pivot_row"]}")
            print(f"Pivot Element: {self.pivot_details["pivot_element"]}")
            print(f"key column: {self.most_negative_variable}")
            print(f"key row: {self.ratio_details['pivot_row_var']}")
            print(f"Lowest Ratio: {self.ratio_details['lowest_ratio']}")
            print("")

    def table_iteration(self):
        # update basis variable
        basis_var_dict = self.nullify_artificials.basis_variables
        self.nullify_artificials.basis_variables = {}
        for var in basis_var_dict:
            if var == self.ratio_details["pivot_row_var"]:
                self.nullify_artificials.basis_variables[self.most_negative_variable] = self.nullify_artificials.cj_dict[self.most_negative_variable]
            else:
                self.nullify_artificials.basis_variables[var] = basis_var_dict[var]


        # update row values in iteration, using the formula F - (RC)/P
        temporary_dict = {}
        for col_index, var in enumerate(self.nullify_artificials.row_dict):
            if var != self.ratio_details["pivot_row_var"]:
                temporary_dict[var] = {
                    item[0] : item[1] - ((self.pivot_details["pivot_column"][col_index] * self.pivot_details["pivot_row"][row_index]) / self.pivot_details["pivot_element"])
                    for row_index, item in enumerate(self.nullify_artificials.row_dict[var].items())
                }
            else:
                temporary_dict[self.most_negative_variable] = {key : value / self.pivot_details["pivot_element"] for key, value in self.nullify_artificials.row_dict[var].items()}

        self.nullify_artificials.row_dict.clear()
        self.nullify_artificials.row_dict.update(temporary_dict)

        # update z and cj - z
        self.nullify_artificials.zj_dict =  self.nullify_artificials.get_z_dict()
        self.nullify_artificials.cj_minus_z_dict = self.nullify_artificials.get_cj_minus_z_dict()

    def solve(self, counter):
        self.get_pivot_details()
        self.table_iteration()
        if self.debug:
            print(f"ITERATION: {counter}")
            self.nullify_artificials.display_table()

    def run_optimisation(self):
        if self.debug:
            print("INITIAL SIMPLEX TABLAEU")
            self.nullify_artificials.display_table()
        counter = 0
        while min(self.nullify_artificials.cj_minus_z_dict.values()) < 0:
            counter += 1
            self.solve(counter)

    def drop_artificials(self):
        # remove all the artificials, except the ones in the basis variable dict
        basis_set = set(self.nullify_artificials.basis_variables.keys())
        artificials = [var for var in self.nullify_artificials.all_variables if var.startswith("artificial") and var not in basis_set]
        for artificial in artificials:
            # delete artificials across all columns
            self.nullify_artificials.all_variables.remove(artificial)
            del self.nullify_artificials.cj_dict[artificial]
            del self.nullify_artificials.zj_dict[artificial]
            del self.nullify_artificials.cj_minus_z_dict[artificial]
            for row in self.nullify_artificials.row_dict:
                del self.nullify_artificials.row_dict[row][artificial]

    def check_feasibility(self) -> bool:
        # solves phase 1
        self.run_optimisation()
        # checking the artificials in the basis variables if any
        for variable in self.nullify_artificials.row_dict:
            if variable.startswith("artificial") and self.nullify_artificials.row_dict[variable]["rhs"] > 0:
                return False
        return True

    def optimize_cost(self) -> tuple:
        if not self.check_feasibility():
            print("Problem is Infeasible, Cannot go ahead with optimisation of cost")
            return "Infeasible", None, None
        print("===" * 300)
        print("PROBLEM IS FEASIBLE")
        print("PHASE 2 : OPTIMISING COST OF INGREDIENTS")
        print("===" * 300)

        self.drop_artificials()
        # changing the cj values to match the objective function
        self.nullify_artificials.cj_dict.clear()
        temporary_dict = {}
        obj_function = self.nullify_artificials.standardize_object.parsed_object.objective_function
        for variable in self.nullify_artificials.all_variables:
            if variable in obj_function:
                temporary_dict[variable] = obj_function[variable]
            else:
                temporary_dict[variable] = 0
        self.nullify_artificials.cj_dict.update(temporary_dict)

        # updating the basis variables to be correlated with the cj
        for variable in self.nullify_artificials.cj_dict:
            if variable in self.nullify_artificials.basis_variables:
                self.nullify_artificials.basis_variables[variable] = self.nullify_artificials.cj_dict[variable]

        # updating z and cj -z rows for the new initial simplex tablaeu
        self.nullify_artificials.zj_dict = self.nullify_artificials.get_z_dict()
        self.nullify_artificials.cj_minus_z_dict = self.nullify_artificials.get_cj_minus_z_dict()
        self.run_optimisation()

        # read out optimal solution
        total_cost = 0
        solution_parts = []
        solution = {}
        for variable in obj_function:
            if variable in self.nullify_artificials.row_dict:
                # ingredient is in the basis
                value = self.nullify_artificials.row_dict[variable]["rhs"]
            else:
                # ingredient not in the basis (non-basic variable)
                value = 0
            solution[variable] = value
            total_cost += obj_function[variable] * value
        return "Optimal", total_cost, solution


class SensitivityAnalysis:

    def __init__(self, simplex_object : SimplexSolver):
        self.simplex_object = simplex_object

    def map_variable_to_constraint(self, variable):
        # this gets the exact constraint in which the variable is in, giving us the nutrient
        nutri_constraint = self.simplex_object.nullify_artificials.standardize_object.nutritional_constraints
        inclusion_lim_constraint =self.simplex_object.nullify_artificials.standardize_object.inclusion_limit_constraints

        # check nutritional constraint first
        for nutrient in nutri_constraint:
            if variable in nutri_constraint[nutrient]["left_hand_side"]:
                return nutrient

        # check inclusion limit constraint next
        for equation in inclusion_lim_constraint:
            if variable in inclusion_lim_constraint[equation]["left_hand_side"]:
                ingredient = list(inclusion_lim_constraint[equation]["left_hand_side"].keys())[0]
                inequality_symbol = inclusion_lim_constraint[equation]["inequality_symbol"]
                suffix = "max" if inequality_symbol == "≤" else "min"
                return f"{ingredient}_{suffix}"
        return None

    def extract_shadow_prices(self):
        shadow_prices = {}
        for variable in self.simplex_object.nullify_artificials.all_variables:
            if variable.startswith("surplus") or variable.startswith("slack"):
                price = self.simplex_object.nullify_artificials.cj_minus_z_dict[variable]
                constraint = self.map_variable_to_constraint(variable)
                shadow_prices[constraint] = price
        return shadow_prices

    def get_reduced_cost(self):
        # this gets the reduced_cost per decision variable from cj - z and if the variable is in the optimal mix form the basis variable
        reduced_cost_dict = {}
        for var in self.simplex_object.nullify_artificials.standardize_object.parsed_object.variables:
            reduced_cost_dict[var] = {
                "reduced_cost": self.simplex_object.nullify_artificials.cj_minus_z_dict.get(var, 0),
                "in_mix": True if var in self.simplex_object.nullify_artificials.row_dict else False
            }
        return reduced_cost_dict

    def format_analysis(self, solution_details):
        TOL = 1e-6
        not_in_mix = []
        if solution_details[0] == "Infeasible":
            return None

        print("SHADOW PRICES (MARGINAL VALUES OF EACH CONSTRAINTS)")
        shadow_prices = self.extract_shadow_prices()
        reduced_cost = self.get_reduced_cost()
        for const in shadow_prices:
            price = shadow_prices[const]
            print(f"{const} | {round(price, 2)} | {"BINDING" if abs(price) > TOL else "not binding" }")
        print("")

        for ingredient in reduced_cost:
            if not reduced_cost[ingredient]["in_mix"]:
                not_in_mix.append(ingredient)
        print("")
        print(f"INGREDIENTS NOT IN MIX: {','.join(not_in_mix)}")
        if len(not_in_mix) == 0:
            print("ALL INGREDIENTS IN MIX")

        print("")
        print("OPTIMAL MIX :")
        for variable in solution_details[2]:
            print(f"{variable} -> {round(solution_details[2][variable], 2)} KG")
        print(f"Total Cost: N{round(solution_details[1], 2)}")
        return ""

    def run_analysis(self):
        solution_details = self.simplex_object.optimize_cost()
        # print(solution_details)
        self.format_analysis(solution_details)


class FeedFormulation:
    def __init__(self, sensitivity_object : SensitivityAnalysis):
        self.sensitivity_object = sensitivity_object

    def run_formulation(self):
        self.sensitivity_object.run_analysis()


path_dict = {
    "ingredients": "/Users/eniola/Desktop/projects_n_stuff/feed_formulation/test_data/ingredients.xlsx",
    "composition": "/Users/eniola/Desktop/projects_n_stuff/feed_formulation/test_data/composition.xlsx",
    "requirements": "/Users/eniola/Desktop/projects_n_stuff/feed_formulation/test_data/requirements.xlsx"
}
max_bal = 100
parsed_data = ParseData(path_dict, max_bal)
standard_data = Standardize(parsed_data)
phase1 = NullifyArtificials(standard_data)
solver = SimplexSolver(phase1, debug=True)
sensitivity_analysis = SensitivityAnalysis(solver)
model = FeedFormulation(sensitivity_analysis)
model.run_formulation()




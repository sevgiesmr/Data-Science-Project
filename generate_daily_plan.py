import pandas as pd
import os

def generate_daily_plan(recipe_costs_path, output_path, num_days=30):
    df = pd.read_excel(recipe_costs_path)
    # Ensure columns are as expected
    df.columns = [col.strip() for col in df.columns]
    breakfasts = df[df['category'].str.lower() == 'breakfast'].reset_index(drop=True)
    lunches = df[df['category'].str.lower() == 'lunch'].reset_index(drop=True)
    dinners = df[df['category'].str.lower() == 'dinner'].reset_index(drop=True)

    # Debug: print unique categories and check for empty categories
    if len(breakfasts) == 0 or len(lunches) == 0 or len(dinners) == 0:
        print("Unique categories found:", df['category'].unique())
        raise ValueError(
            f"One or more meal categories are empty! "
            f"Breakfasts: {len(breakfasts)}, Lunches: {len(lunches)}, Dinners: {len(dinners)}. "
            "Check your category column values in recipe_total_costs.xlsx."
        )

    plan_rows = []
    for day in range(num_days):
        b_idx = day % len(breakfasts)
        l_idx = day % len(lunches)
        d_idx = day % len(dinners)
        b = breakfasts.iloc[b_idx]
        l = lunches.iloc[l_idx]
        d = dinners.iloc[d_idx]
        total = b['cost'] + l['cost'] + d['cost']
        plan_rows.append({
            'day': day + 1,
            'breakfast_name': b['recipe_name'],
            'breakfast_cost': b['cost'],
            'lunch_name': l['recipe_name'],
            'lunch_cost': l['cost'],
            'dinner_name': d['recipe_name'],
            'dinner_cost': d['cost'],
            'total_cost': total
        })
    plan_df = pd.DataFrame(plan_rows)
    plan_df.to_excel(output_path, index=False)

if __name__ == "__main__":
    input_path = os.path.join("output", "recipe_total_costs.xlsx")
    output_path = os.path.join("output", "daily_plan.xlsx")
    generate_daily_plan(input_path, output_path, num_days=30) 
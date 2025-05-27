import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def create_visualizations(meal_costs, daily_costs, monthly_total):
    """Create and save visualizations of the cost distribution"""
    # Create output directory for plots
    plots_dir = os.path.join("output", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Set style
    plt.style.use('default')
    sns.set_theme()
    colorblind_palette = sns.color_palette('colorblind')
    
    # 1. Daily Cost Trend
    plt.figure(figsize=(12, 6))
    plt.plot(daily_costs['Day'], daily_costs['Total Daily Cost'], marker='o', color=colorblind_palette[0])
    plt.axhline(y=monthly_total/30, color=colorblind_palette[1], linestyle='--', label='Average Daily Cost')
    plt.title('Daily Cost Trend', fontsize=14, pad=15)
    plt.xlabel('Day', fontsize=12)
    plt.ylabel('Cost (TL)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'daily_cost_trend.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Meal Type Distribution
    meal_type_costs = pd.DataFrame([
        {'Meal Type': meal_type, 'Cost': cost}
        for costs in daily_costs['Meal Costs']
        for meal_type, cost in costs.items()
    ])
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Meal Type', y='Cost', data=meal_type_costs, palette='colorblind')
    plt.title('Cost Distribution by Meal Type', fontsize=14, pad=15)
    plt.xlabel('Meal Type', fontsize=12)
    plt.ylabel('Cost (TL)', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'meal_type_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Cost Breakdown Pie Chart
    meal_type_totals = meal_type_costs.groupby('Meal Type')['Cost'].sum()
    plt.figure(figsize=(8, 8))
    plt.pie(meal_type_totals, labels=meal_type_totals.index, autopct='%1.1f%%',
            colors=colorblind_palette[:len(meal_type_totals)], textprops={'fontsize': 12})
    plt.title('Total Cost Distribution by Meal Type', fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'cost_breakdown_pie.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Top 10 Most Expensive Meals
    top_meals = meal_costs.nlargest(10, 'cost')
    plt.figure(figsize=(12, 6))
    bars = plt.barh(top_meals['recipe_name'], top_meals['cost'], color=colorblind_palette[:len(top_meals)])
    plt.title('Top 10 Most Expensive Meals', fontsize=14, pad=15)
    plt.xlabel('Cost (TL)', fontsize=12)
    plt.ylabel('Recipe', fontsize=12)
    # Add value labels on the bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, f'{width:.2f} TL',
                ha='left', va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'top_expensive_meals.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Weekly Cost Trend
    daily_costs['Week'] = (daily_costs['Day'] - 1) // 7 + 1
    weekly_costs = daily_costs.groupby('Week')['Total Daily Cost'].mean()
    
    plt.figure(figsize=(10, 6))
    weekly_costs.plot(kind='bar', color=colorblind_palette[:len(weekly_costs)])
    plt.title('Average Daily Cost by Week', fontsize=14, pad=15)
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Average Daily Cost (TL)', fontsize=12)
    plt.grid(True, alpha=0.3)
    # Add value labels on top of bars
    for i, v in enumerate(weekly_costs):
        plt.text(i, v, f'{v:.2f} TL', ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'weekly_cost_trend.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    return plots_dir

def calculate_meal_costs():
    print("Loading meal plan with calculated costs...")
    
    # Read the meal plan with calculated costs
    input_file = os.path.join("output", "meal_plan_with_calculated_costs.xlsx")
    df = pd.read_excel(input_file)
    
    # Group by day and category (meal type) to get meal costs
    meal_costs = df.groupby(['day', 'category', 'recipe_name'])['cost'].sum().reset_index()
    
    # Calculate daily totals
    daily_costs = meal_costs.groupby('day').agg({
        'category': lambda x: dict(zip(x, meal_costs.loc[x.index, 'cost'])),
        'cost': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    daily_costs.columns = ['Day', 'Meal Costs', 'Total Daily Cost']
    
    # Calculate monthly total
    monthly_total = daily_costs['Total Daily Cost'].sum()
    
    # Calculate meal type averages
    meal_type_averages = {}
    for meal_type in ['breakfast', 'lunch', 'dinner']:
        meal_costs_type = [costs.get(meal_type, 0) for costs in daily_costs['Meal Costs']]
        meal_type_averages[meal_type] = sum(meal_costs_type) / len(meal_costs_type)
    
    # Find most expensive and cheapest meals
    meal_costs_with_names = meal_costs.copy()
    meal_costs_with_names['full_name'] = meal_costs_with_names.apply(
        lambda x: f"{x['recipe_name']} ({x['category']}, Day {x['day']})", axis=1
    )
    
    most_expensive_meals = meal_costs_with_names.nlargest(5, 'cost')
    cheapest_meals = meal_costs_with_names.nsmallest(5, 'cost')
    
    # Create visualizations
    plots_dir = create_visualizations(meal_costs, daily_costs, monthly_total)
    
    # Save detailed meal costs
    meal_costs_file = os.path.join("output", "recipe_total_costs.xlsx")
    meal_costs.to_excel(meal_costs_file, index=False)
    print(f"Detailed recipe costs saved to: {meal_costs_file}")
    
    # Save daily costs
    daily_costs_file = os.path.join("output", "daily_costs_per_month.xlsx")
    daily_costs.to_excel(daily_costs_file, index=False)
    print(f"Daily costs saved to: {daily_costs_file}")
    
    # Print summary statistics
    print("\n=== COST SUMMARY ===")
    print(f"Total monthly cost: {monthly_total:.2f} TL")
    print(f"Average daily cost: {monthly_total/30:.2f} TL")
    
    print("\n=== MEAL TYPE AVERAGES ===")
    for meal_type, avg_cost in meal_type_averages.items():
        print(f"Average {meal_type} cost: {avg_cost:.2f} TL")
    
    print("\n=== MOST EXPENSIVE MEALS ===")
    for _, meal in most_expensive_meals.iterrows():
        print(f"{meal['full_name']}: {meal['cost']:.2f} TL")
    
    print("\n=== CHEAPEST MEALS ===")
    for _, meal in cheapest_meals.iterrows():
        print(f"{meal['full_name']}: {meal['cost']:.2f} TL")
    
    print("\n=== VISUALIZATIONS ===")
    print(f"Cost distribution plots saved to: {plots_dir}")
    
    # Print daily breakdown
    print("\n=== DAILY COST BREAKDOWN ===")
    for _, row in daily_costs.iterrows():
        print(f"\nDay {row['Day']}:")
        print(f"  Total: {row['Total Daily Cost']:.2f} TL")
        for meal_type, cost in row['Meal Costs'].items():
            print(f"  {meal_type}: {cost:.2f} TL")

if __name__ == "__main__":
    calculate_meal_costs() 
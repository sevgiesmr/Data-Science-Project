import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys

# Kitchen unit conversions
KITCHEN_UNIT_TO_GRAM = {
    'yemek kaşığı': 15,
    'tatlı kaşığı': 5,
    'çay kaşığı': 2.5,
    'su bardağı': 200,
    'çay bardağı': 100,
    'fincan': 65,
    'avuç': 25,
    'tutam': 2.5,
    'kase': 200,  # Added for "kase" unit
    'demet': 100,  # Added for "demet" unit
    'baş': 50,    # Added for "baş" unit (e.g., sarımsak)
    'diş': 5,     # Added for "diş" unit (e.g., sarımsak)
    'paket': 10,  # Added for "paket" unit (e.g., kabartma tozu)
}
KITCHEN_UNIT_TO_ML = {
    'yemek kaşığı': 15,
    'tatlı kaşığı': 5,
    'çay kaşığı': 2.5,
    'su bardağı': 200,
    'çay bardağı': 100,
    'fincan': 65,
}

# Average weights (grams) for common vegetables/fruits sold as "adet"
ADET_TO_GRAM = {
    'domates': 150,  # medium tomato
    'salatalık': 120,  # medium cucumber
    'soğan': 130,  # medium onion
    'patates': 150,  # medium potato
    'biber': 40,  # medium pepper
    'kapya biber': 100,  # large red pepper
    'yeşil biber': 30,  # medium green pepper
    'patlıcan': 200,  # medium eggplant
    'elma': 180,  # medium apple
    'portakal': 200,  # medium orange
    'limon': 80,  # medium lemon
    'muz': 120,  # medium banana
    'yumurta': 60,  # medium egg
    'lavaş': 100,  # one piece of lavash
    'yufka': 50,   # one piece of yufka
}

# Known liquids (expand as needed)
KNOWN_LIQUIDS = [
    'su', 'süt', 'zeytinyağı', 'ayçiçek yağı', 'sıvı yağ', 'sıvıyağ', 'sirke', 'limon suyu', 'nar ekşisi', 'soda', 'sos', 'bal', 'pekmez', 'yoğurt', 'krema', 'salça', 'ketçap', 'mayonez', 'tereyağı', 'margarin'
]

# Ingredients that should be treated as solids even if they're in the liquids list
SOLID_INGREDIENTS = [
    'salça', 'tereyağı', 'margarin', 'bal', 'pekmez', 'yoğurt', 'krema'
]

def convert_to_kg_or_lt(amount, unit, ingredient_name, price_unit=None):
    # Handle empty units for common ingredients
    if not unit:
        if any(spice in ingredient_name for spice in ['tuz', 'karabiber', 'kırmızı pul biber', 'kırmızı toz biber', 'kekik', 'kimyon', 'nane']):
            return 0.01, 'kg'  # Assume 10g for spices
        elif 'maydanoz' in ingredient_name:
            return 0.01, 'kg'  # Assume 10g for herbs
        elif 'sarımsak' in ingredient_name:
            return 0.01, 'kg'  # Assume 10g for garlic
        elif 'peynir' in ingredient_name:
            return 0.05, 'kg'  # Assume 50g for cheese
        elif any(liquid in ingredient_name for liquid in KNOWN_LIQUIDS):
            if any(solid in ingredient_name for solid in SOLID_INGREDIENTS):
                return 0.05, 'kg'  # Treat as solid
            return 0.1, 'lt'  # Assume 100ml for liquids
        return None, unit

    # Handle kitchen units
    is_liquid = any(liquid in ingredient_name for liquid in KNOWN_LIQUIDS) and not any(solid in ingredient_name for solid in SOLID_INGREDIENTS)
    
    if unit in KITCHEN_UNIT_TO_GRAM and not is_liquid:
        grams = amount * KITCHEN_UNIT_TO_GRAM[unit]
        return grams / 1000, 'kg'
    elif unit in KITCHEN_UNIT_TO_ML and is_liquid:
        mls = amount * KITCHEN_UNIT_TO_ML[unit]
        return mls / 1000, 'lt'
    elif unit == 'g':
        return amount / 1000, 'kg'
    elif unit == 'kg':
        return amount, 'kg'
    elif unit == 'ml':
        return amount / 1000, 'lt'
    elif unit == 'lt':
        return amount, 'lt'
    elif unit == 'adet':
        if price_unit == 'adet':
            return amount, 'adet'
        elif price_unit == 'kg':
            # Try to convert adet to kg using average weight
            for key, avg_weight in ADET_TO_GRAM.items():
                if key in ingredient_name:
                    grams = amount * avg_weight
                    return grams / 1000, 'kg'
            return None, unit  # cannot convert if not in dictionary
        else:
            return None, unit
    else:
        return None, unit  # fallback

def calculate_cost(recipe_amount, recipe_unit, price, price_amount, price_unit, ingredient_name):
    """
    Calculate the cost of an ingredient based on recipe amount and price information.
    Returns (cost, converted_amount, final_unit, debug_message)
    """
    # Convert recipe amount to match price unit
    converted_amount, final_unit = convert_to_kg_or_lt(recipe_amount, recipe_unit, ingredient_name, price_unit)
    
    if converted_amount is None:
        return None, None, None, f"unit conversion failed: {recipe_amount} {recipe_unit} to {price_unit}"
    
    if price_amount == 0:
        return None, converted_amount, final_unit, "price_amount is zero"
    
    if final_unit != price_unit:
        return None, converted_amount, final_unit, f"unit mismatch: recipe {final_unit}, price {price_unit}"
    
    # Calculate unit price and total cost
    try:
        unit_price = price / price_amount
        cost = unit_price * converted_amount
        return cost, converted_amount, final_unit, "success"
    except Exception as e:
        return None, converted_amount, final_unit, f"calculation error: {str(e)}"

def main():
    print("Starting cost calculation process...")
    # Default file names
    meal_plan_file = 'meal_plan.json'
    ingredients_file = 'unique_ingredients2.xlsx'
    # Use arguments if provided
    if len(sys.argv) > 2:
        meal_plan_file = sys.argv[1]
        ingredients_file = sys.argv[2]
    print(f"Using meal plan file: {meal_plan_file}")
    print(f"Using ingredients file: {ingredients_file}")
    # Load the DataFrame from the ingredients Excel file
    print("Loading ingredient price data...")
    price_df = pd.read_excel(ingredients_file, usecols=["Ingredient", "price", "amount", "unit"])
    price_df['Ingredient_clean'] = price_df['Ingredient'].str.lower().str.strip()
    print(f"Loaded {len(price_df)} ingredients with prices")

    # Load meal plan from the provided JSON file
    print("\nLoading meal plan data...")
    with open(meal_plan_file, 'r', encoding='utf-8') as f:
        meal_plan_json = json.load(f)
    meal_plan = meal_plan_json['meal_plan']  # This is a list of days
    print(f"Loaded meal plan with {len(meal_plan)} days")

    results = []
    debug_log = []
    SIMILARITY_THRESHOLD = 0.7

    print("\nProcessing meals and calculating costs...")
    for day_obj in meal_plan:
        day = day_obj.get('day')
        print(f"\nProcessing day: {day}")
        for meal_type, recipe in day_obj.items():
            if meal_type == 'day':
                continue
            if not recipe or not isinstance(recipe, dict):
                continue
            recipe_name = recipe.get('name', recipe.get('title', 'Unknown Recipe'))
            print(f"  Processing {meal_type}: {recipe_name}")
            for ingredient in recipe.get('ingredients', []):
                ing_text = ingredient.get('text', '').strip().lower()
                ing_amount = ingredient.get('amount', 1)
                ing_unit = ingredient.get('unit', '').strip().lower()
                if not ing_text:
                    continue
                # TF-IDF match
                vectorizer = TfidfVectorizer().fit(list(price_df['Ingredient_clean']))
                price_vecs = vectorizer.transform(price_df['Ingredient_clean'])
                ing_vec = vectorizer.transform([ing_text])
                sims = cosine_similarity(ing_vec, price_vecs).flatten()
                best_idx = sims.argmax()
                best_score = sims[best_idx]
                if best_score >= SIMILARITY_THRESHOLD:
                    matched_row = price_df.iloc[best_idx]
                    price = matched_row['price']
                    price_amount = matched_row['amount']
                    price_unit = matched_row['unit'].strip().lower()
                    cost, converted_amount, final_unit, debug_reason = calculate_cost(
                        ing_amount, ing_unit, price, price_amount, price_unit, ing_text)
                    match_status = "Matched"
                else:
                    matched_row = None
                    price = None
                    price_amount = None
                    price_unit = None
                    cost = None
                    converted_amount = None
                    final_unit = None
                    match_status = "Not found"
                    debug_reason = "no good match (low similarity)"
                result = {
                    'day': day,
                    'category': meal_type,
                    'recipe_name': recipe_name,
                    'meal_ingredient': ing_text,
                    'matched_ingredient': matched_row['Ingredient'] if matched_row is not None else None,
                    'score': best_score,
                    'recipe_amount': ing_amount,
                    'recipe_unit': ing_unit,
                    'price': price,
                    'price_amount': price_amount,
                    'price_unit': price_unit,
                    'converted_amount': converted_amount,
                    'final_unit': final_unit,
                    'cost': cost,
                    'match_status': match_status,
                    'debug_issue': debug_reason
                }
                results.append(result)
                if cost is None:
                    debug_log.append(result)

    print(f"\nProcessed {len(results)} ingredients in total")
    print(f"Found {len(debug_log)} ingredients with missing costs")

    results_df = pd.DataFrame(results)
    os.makedirs("output", exist_ok=True)
    output_file = os.path.join("output", "meal_plan_with_calculated_costs.xlsx")
    results_df.to_excel(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

    print("\nProcessing complete!")

if __name__ == "__main__":
    main() 
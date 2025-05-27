import json
import re
from openpyxl import Workbook

REMOVE_WORDS = [
    "az", "dolusu", "biraz", "bir", "yarım", "çeyrek", "orta", "büyük", "küçük", "silme",
    "adet", "orta boy", "baş", "gr", "g", "kg", "yemek kaşığı", "çay kaşığı",
    "su bardağı", "tatlı kaşığı", "paket", "dilim", "bardak", "kaşık", "fincan",
    "çorba kaşığı", "küçük boy", "büyük boy", "tane", "diş", "kase", "avuç", "demet", "tutam", "parça", "bardağı"
]
PHRASES_TO_REMOVE = [
    "üzeri için", "sosu için", "sos için"
]

def clean_ingredient(text):
    text = text.lower()
    # Remove anything in parentheses
    text = re.sub(r"\([^)]*\)", "", text)
    # Remove trailing colons and spaces
    text = text.strip(" :")
    # Remove phrases
    for phrase in PHRASES_TO_REMOVE:
        text = text.replace(phrase, "")
    # Remove if 'için' is anywhere in the string
    if "için" in text:
        return ""
    # Remove all numbers and fractions
    text = re.sub(r"\d+[.,/]?\d*\s*", "", text)
    # Remove all REMOVE_WORDS even if they are concatenated with other words
    for word in REMOVE_WORDS:
        text = re.sub(rf"{re.escape(word)}", " ", text)
    # Remove multiple spaces and trailing colons
    text = re.sub(r"\s+", " ", text).strip(" :")
    return text

with open('meal_plan.json', 'r', encoding='utf-8') as f:
    meal_plan = json.load(f)

unique_ingredients = set()

for category in meal_plan.values():
    for recipe in category:
        for ingredient in recipe.get('ingredients', []):
            text = ingredient.get('text', '').strip()
            if text:
                cleaned = clean_ingredient(text)
                if cleaned:
                    unique_ingredients.add(cleaned)

# Write to Excel
wb = Workbook()
ws = wb.active
ws.title = "Unique Ingredients"
ws.append(["Ingredient"])

for ingredient in sorted(unique_ingredients):
    ws.append([ingredient])

wb.save("unique_ingredients.xlsx")
print("Unique ingredients have been written to unique_ingredients.xlsx") 
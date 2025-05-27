from bs4 import BeautifulSoup
import requests
import json
import os
import re
import time
from urllib.parse import urlparse, unquote
import random

def get_recipe_name_from_url(url):
    """Extract recipe name from URL"""
    path = urlparse(url).path
    recipe_name = path.split('/')[-1]
    # Just decode the URL and format the title
    recipe_name = unquote(recipe_name).replace('-', ' ').title()
    return recipe_name

def parse_amount(ingredient_text):
    """Parse amount and unit from ingredient text"""
    units = {
        'kg': 1000, 'g': 1, 'gr': 1, 'gram': 1,
        'lt': 1000, 'ml': 1, 'cc': 1,
        'adet': 1, 'tane': 1, 
        'çay kaşığı': 5,
        'yemek kaşığı': 15,
        'su bardağı': 200,
        'fincan': 100,
        'tatlı kaşığı': 10
    }
    
    amount = 1
    unit = ''  # Empty string as default unit
    
    numbers = re.findall(r'\d+(?:[.,]\d+)?', ingredient_text)
    if numbers:
        amount = float(numbers[0].replace(',', '.'))
    
    for unit_name, multiplier in units.items():
        if unit_name in ingredient_text.lower():
            unit = unit_name
            break
    
    return amount, unit

def get_recipe_links(category_url):
    """Scrape recipe links from ye-mek.net"""
    links = []
    seen_names = set()  # Keep track of recipe names we've seen
    current_page = 1
    
    try:
        while True:
            # Construct the URL for the current page
            if current_page == 1:
                page_url = category_url
            else:
                page_url = f"{category_url}-{current_page}"
            
            print(f"\nScraping page {current_page}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(page_url, headers=headers)
            response.encoding = 'utf-8'  # Ensure proper Turkish character encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for recipe links in the main content area
            recipe_links = soup.select("div.entry-content a[href*='/tarif/']")
            if not recipe_links:
                # If no links found in entry-content, try the whole page
                recipe_links = soup.select("a[href*='/tarif/']")
            
            # Check if we found any recipes on this page
            if not recipe_links:
                print(f"No recipes found on page {current_page}")
                break
            
            print(f"Found {len(recipe_links)} potential recipe links on page {current_page}")
            
            # Process recipes from current page
            for link in recipe_links:
                href = link.get('href')
                if href and '/tarif/' in href:
                    full_url = f"https://ye-mek.net{href}" if href.startswith('/') else href
                    recipe_name = get_recipe_name_from_url(full_url)
                    # Only add if we haven't seen this recipe name before
                    if recipe_name not in seen_names:
                        seen_names.add(recipe_name)
                        links.append({
                            'url': full_url,
                            'name': recipe_name
                        })
                        print(f"Added recipe: {recipe_name}")
            
            # Look for the "İleri" (Next) button
            next_button = soup.select_one('a[title*="İleri"]')
            if not next_button:
                print("No more pages found")
                break
            
            current_page += 1
            time.sleep(1)  # Be nice to the server
        
        print(f"\nTotal unique recipes found across all pages: {len(links)}")
        
    except Exception as e:
        print(f"Error getting recipe links: {str(e)}")
    
    return links

def get_recipe_details(recipe_info):
    """Scrape recipe details including ingredients"""
    url = recipe_info['url']
    recipe_name = recipe_info['name']
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'  # Ensure proper Turkish character encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.select_one("h1.entry-title")
        title = title.text.strip() if title else recipe_name
        
        ingredients = []
        ingredient_list = soup.select('li[itemprop="recipeIngredient"]')
        for ingredient in ingredient_list:
            ingredient_text = ingredient.get_text(strip=True)
            amount, unit = parse_amount(ingredient_text)
            ingredients.append({
                'text': ingredient_text,
                'amount': amount,
                'unit': unit
            })
        
        instructions = []
        instruction_list = soup.select("div.instructions ol li")
        for instruction in instruction_list:
            instruction_text = instruction.text.strip()
            instructions.append(instruction_text)
        
        return {
            'title': title,
            'name': recipe_name,
            'ingredients': ingredients,
            'instructions': instructions,
            'url': url
        }
    except Exception as e:
        print(f"Error getting recipe details from {url}: {str(e)}")
        return None

def create_meal_plan(breakfast_recipes, main_course_recipes, days=30):
    """Create a 30-day meal plan"""
    meal_plan = []
    
    # Ensure we have enough recipes
    if len(breakfast_recipes) < days or len(main_course_recipes) < days * 2:
        print("Warning: Not enough recipes for a complete meal plan")
        return None
    
    # Create copies of recipe lists to avoid modifying originals
    available_breakfast = breakfast_recipes.copy()
    available_main_course = main_course_recipes.copy()
    
    # Randomly select recipes for each day
    for day in range(1, days + 1):
        # If we're running low on recipes, replenish the available recipes
        if len(available_breakfast) < 1:
            available_breakfast = breakfast_recipes.copy()
        if len(available_main_course) < 2:
            available_main_course = main_course_recipes.copy()
        
        # Select and remove breakfast recipe
        breakfast = random.choice(available_breakfast)
        available_breakfast.remove(breakfast)
        
        # Select and remove lunch recipe
        lunch = random.choice(available_main_course)
        available_main_course.remove(lunch)
        
        # Select and remove dinner recipe
        dinner = random.choice(available_main_course)
        available_main_course.remove(dinner)
        
        meal_plan.append({
            'day': day,
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner
        })
    
    return meal_plan

def save_recipes(recipes, filename="recipes.json"):
    """Save recipes to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

def main():
    try:
        # Get breakfast recipes
        print("Scraping breakfast recipes...")
        breakfast_links = get_recipe_links("https://ye-mek.net/kahvaltiliklar")
        print(f"Found {len(breakfast_links)} breakfast recipes")
        
        if len(breakfast_links) < 30:
            print("Warning: Not enough breakfast recipes found. Trying alternative URL...")
            # Try alternative URL for breakfast recipes
            breakfast_links = get_recipe_links("https://ye-mek.net/kahvalti-tarifleri")
            print(f"Found {len(breakfast_links)} breakfast recipes from alternative URL")
        
        breakfast_recipes = []
        # Only collect 30 breakfast recipes
        i = 0
        while len(breakfast_recipes) < 30 and i < len(breakfast_links):
            recipe_info = breakfast_links[i]
            print(f"\nScraping breakfast recipe {len(breakfast_recipes) + 1}/30: {recipe_info['name']}")
            recipe = get_recipe_details(recipe_info)
            if recipe:
                breakfast_recipes.append(recipe)
                print(f"Successfully scraped: {recipe['title']}")
            else:
                print(f"Failed to scrape recipe: {recipe_info['name']}")
            i += 1
            time.sleep(1)
        
        # Get main course recipes
        print("\nScraping main course recipes...")
        main_course_links = get_recipe_links("https://ye-mek.net/ana-yemek-tarifleri")
        print(f"Found {len(main_course_links)} main course recipes")
        
        # Try alternative URLs for main course recipes if needed
        if len(main_course_links) < 60:
            print("Warning: Not enough main course recipes found. Trying alternative URLs...")
            
            # Try meat dishes
            print("\nTrying meat dishes...")
            meat_links = get_recipe_links("https://ye-mek.net/et-yemekleri")
            print(f"Found {len(meat_links)} meat recipes")
            main_course_links.extend(meat_links)
            
            # If still not enough, try vegetable dishes
            if len(main_course_links) < 60:
                print("\nTrying vegetable dishes...")
                veg_links = get_recipe_links("https://ye-mek.net/sebze-yemekleri")
                print(f"Found {len(veg_links)} vegetable recipes")
                main_course_links.extend(veg_links)
            
            print(f"Total main course recipes found across all categories: {len(main_course_links)}")
        
        main_course_recipes = []
        # Only collect 60 main course recipes
        i = 0
        while len(main_course_recipes) < 60 and i < len(main_course_links):
            recipe_info = main_course_links[i]
            print(f"\nScraping main course recipe {len(main_course_recipes) + 1}/60: {recipe_info['name']}")
            recipe = get_recipe_details(recipe_info)
            if recipe:
                main_course_recipes.append(recipe)
                print(f"Successfully scraped: {recipe['title']}")
            else:
                print(f"Failed to scrape recipe: {recipe_info['name']}")
            i += 1
            time.sleep(1)
        
        print(f"\nTotal breakfast recipes collected: {len(breakfast_recipes)}")
        print(f"Total main course recipes collected: {len(main_course_recipes)}")
        
        if len(breakfast_recipes) < 30 or len(main_course_recipes) < 60:
            print("Error: Could not collect enough recipes for a complete meal plan.")
            return
        
        # Create meal plan
        print("\nCreating 30-day meal plan...")
        meal_plan = create_meal_plan(breakfast_recipes, main_course_recipes)
        
        if not meal_plan:
            print("Error: Could not create meal plan. Not enough unique recipes.")
            return
        
        # Save all data
        data = {
            'breakfast_recipes': breakfast_recipes,
            'main_course_recipes': main_course_recipes,
            'meal_plan': meal_plan
        }
        save_recipes(data, "meal_plan.json")
        
        print("\nSaved recipes and meal plan to meal_plan.json")
        
        # Print sample day
        if meal_plan:
            print("\nSample Day from Meal Plan:")
            day = meal_plan[0]
            print(f"\nDay {day['day']}:")
            print(f"Breakfast: {day['breakfast']['title']}")
            print(f"Lunch: {day['lunch']['title']}")
            print(f"Dinner: {day['dinner']['title']}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()


import pandas as pd
import speech_recognition as sr
from fuzzywuzzy import fuzz

# Initialize the recognizer
recognizer = sr.Recognizer()

# Load the recipe dataset
def load_recipe_dataset(file_path):
    return pd.read_csv(file_path)

# Function to search for recipes based on user input ingredients
def search_recipes(recipe_df, ingredients):
    matched_recipes = []
    for index, row in recipe_df.iterrows():
        recipe_ingredients = eval(row['ingredients'])  # Extracting ingredients from dataset
        match_ratio = max(fuzz.ratio(ingredient, recipe_ingredient) for ingredient in ingredients for recipe_ingredient in recipe_ingredients)
        if match_ratio > 80:  # Adjust the threshold as needed
            matched_recipes.append(row['title'])
    return matched_recipes

# Function to listen to user's speech input
def listen_for_speech(timeout=300):
    with sr.Microphone() as source:
        print("Listening for speech...")
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.listen(source, timeout=timeout)
    
    try:
        print("Recognizing speech...")
        user_input = recognizer.recognize_google(audio_data, language="en-US", show_all=True)  # Language can be adjusted
        recognized_text = user_input['alternative'][0]['transcript'].lower()  # Extract recognized text
        confidence = user_input['alternative'][0]['confidence']  # Extract confidence score
        print("Recognized:", recognized_text)
        print("Confidence:", confidence)
        return recognized_text, confidence
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return "", 0
    except sr.RequestError:
        print("Sorry, could not request results from Google Speech Recognition service. Check your internet connection.")
        return "", 0

# Main function
def main():
    # Load recipe dataset
    recipe_df = load_recipe_dataset('D:/PU/Sem. 5/AI/Exercise/finalproject/RecipeNLG_dataset.csv')
    
    # Listen for the ingredients the user has
    print("Please speak the ingredients you have.")
    ingredients_input, _ = listen_for_speech()
    
    # Process user input
    if ingredients_input:
        user_input_ingredients = ingredients_input.split()
        
        # Search for recipes based on user input ingredients
        matched_recipes = search_recipes(recipe_df, user_input_ingredients)
        
        # Print matched recipes
        if matched_recipes:
            print("Recipes you can cook with the ingredients you have:")
            for index, recipe in enumerate(matched_recipes, start=1):
                print(f"{index}. {recipe}")
        else:
            print("No recipes found with the given ingredients.")
    else:
        print("No ingredients detected.")

if __name__ == "__main__":
    main()

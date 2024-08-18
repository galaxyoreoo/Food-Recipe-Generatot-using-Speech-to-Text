import pandas as pd
import speech_recognition as sr
from googletrans import Translator

# Initialize the recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Supported language codes for speech recognition
SUPPORTED_LANGUAGES = {
    '1': 'en',   # English
    '2': 'id',   # Indonesian
    '3': 'ja',   # Japanese
    '4': 'ko',   # Korean
    '5': 'zh'    # Chinese
}

# Load the recipe dataset
def load_recipe_dataset(file_path):
    return pd.read_csv(file_path)

# Function to search for recipes based on user input ingredients and sort by likes
def search_recipes_with_sort(recipe_df, ingredients):
    matched_recipes = []
    for index, row in recipe_df.iterrows():
        recipe_ingredients = row['Ingredients']
        if pd.notna(recipe_ingredients) and any(ingredient.lower() in recipe_ingredients.lower() for ingredient in ingredients):
            matched_recipes.append(row)
        matched_recipes.sort(key=lambda x: x['Loves'], reverse=True)

    return matched_recipes


# Function to listen to user's speech input
def listen_for_speech(timeout=300, language="en-US"):
    with sr.Microphone() as source:
        print("Listening for speech...")
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.listen(source, timeout=timeout)
    
    try:
        print("Recognizing speech...")
        user_input = recognizer.recognize_google(audio_data, language=language, show_all=True)  # Language can be adjusted
        recognized_text = user_input['alternative'][0]['transcript'].lower()  # Extract recognized text
        confidence = user_input['alternative'][0]['confidence']  # Extract confidence score
        
        # Translate recognized text to English if not already in English
        if language != "en-US":
            translated_text = translator.translate(recognized_text, src=language, dest='id').text
            print("Recognized (Translated to Indonesian):", translated_text)
            return translated_text, confidence
        else:
            print("Recognized:", recognized_text)
            return recognized_text, confidence
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return "", 0
    except sr.RequestError:
        print("Sorry, could not request results from Google Speech Recognition service. Check your internet connection.")
        return "", 0

# Function to get user's preferred language
def get_preferred_language():
    while True:
        print("Please select your preferred language:")
        for code, lang in SUPPORTED_LANGUAGES.items():
            print(f"{code}. {lang}")
        choice = input("Enter the number corresponding to your choice: ")
        if choice in SUPPORTED_LANGUAGES:
            return SUPPORTED_LANGUAGES[choice]
        else:
            print("Invalid choice. Please select a valid number.")

# Translate text to the specified language
def translate_to_language(text, language):
    translated_text = translator.translate(text, dest=language).text
    return translated_text

# Main function
def main():
    # Load recipe dataset
    try:
        recipe_df = load_recipe_dataset('indonesianfoods.csv')  # Adjust the file path if necessary
    except FileNotFoundError:
        print("Dataset file not found. Please ensure the file path is correct.")
        return
    
    # Get user's preferred language
    preferred_language = get_preferred_language()
    
    # Listen for the ingredients the user has
    print("Please speak the ingredients you have.")
    ingredients_input, _ = listen_for_speech(language=preferred_language)
    
    # Process user input
    if ingredients_input:
        user_input_ingredients = ingredients_input.split()
        
        # Search for recipes based on user input ingredients and sort by likes
        matched_recipes = search_recipes_with_sort(recipe_df, user_input_ingredients)
        
        # Print matched recipes
        if matched_recipes:
            print("Matched recipes:")
            for index, recipe in enumerate(matched_recipes[:100], start=1):  # Limit to the first 100 recipes
                translated_recipe_title = translate_to_language(recipe['Title'], preferred_language)
                print(f"{index}. {translated_recipe_title} (Loves: {recipe['Loves']})")

            # Ask the user to choose a recipe
            print("Please say the number of the recipe you want to choose.")
            
            # Listen for recipe choice with a 5-minute timeout
            retries = 3  # Number of retries allowed
            while retries > 0:
                recipe_choice_text, _ = listen_for_speech(timeout=300, language=preferred_language)  # Use preferred language for recipe choice
                
                try:
                    recipe_choice_index = int(recipe_choice_text) - 1
                    chosen_recipe = matched_recipes[recipe_choice_index]
                    break  # Exit the loop if the index is valid
                except (ValueError, IndexError):
                    retries -= 1
                    if retries > 0:
                        print(f"Sorry, the specified recipe number is invalid or does not exist. You have {retries} {'tries' if retries > 1 else 'try'} left. Please try again.")
                    else:
                        print("Sorry, you have exceeded the maximum number of retries. Exiting.")
                        return
            
            # Print the chosen recipe, its ingredients, and directions
            if chosen_recipe is not None and not chosen_recipe.empty:
                print(f"You have chosen {chosen_recipe['Title']}.")
                ingredients = chosen_recipe['Ingredients']
                directions = chosen_recipe['Steps']
                
                # Translate ingredients and directions to preferred language
                translated_ingredients = translate_to_language(ingredients, preferred_language)
                translated_directions = translate_to_language(directions, preferred_language)
                
                print("\nIngredients:")
                print(translated_ingredients)
                
                print("\nDirections:")
                print(translated_directions)
                
                # Ask if the user needs anything else
                print("\nDo you need anything else?")
                response, _ = listen_for_speech(language=preferred_language)
                if "no" in response.lower():
                    return  # Exit the program if the user doesn't need anything else
            else:
                print("Sorry, the specified recipe number is invalid or does not exist.")
        else:
            print("No recipes found with the given ingredients.")
    else:
        print("No input detected.")

if __name__ == "__main__":
    main()

import json
import os
import base64
import requests
from langchain.tools import tool
from ibm_watsonx_ai import Credentials, APIClient
from ibm_watsonx_ai.foundation_models import ModelInference
from io import BytesIO
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)

credentials = Credentials(url="https://us-south.ml.cloud.ibm.com")
client = APIClient(credentials)
project_id = "skills-network"


def _encode_image(image_input: str) -> str:
    """Helper — encodes a local file or URL to base64."""
    if image_input.startswith("http"):
        response = requests.get(image_input)
        response.raise_for_status()
        image_bytes = BytesIO(response.content)
    else:
        if not os.path.isfile(image_input):
            raise FileNotFoundError(f"No file found at path: {image_input}")
        with open(image_input, "rb") as f:
            image_bytes = BytesIO(f.read())
    return base64.b64encode(image_bytes.read()).decode("utf-8")


class ExtractIngredientsTool:
    @tool("Extract ingredients")
    def extract_ingredient(image_input: str):
        """
        Extract ingredients from a food item image.

        :param image_input: The image file path (local) or URL (remote).
        :return: A list of ingredients extracted from the image.
        """
        logging.info("Extracting ingredients from image...")
        encoded_image = _encode_image(image_input)

        model = ModelInference(
            model_id="meta-llama/llama-3-2-90b-vision-instruct",
            credentials=credentials,
            project_id=project_id,
            params={"max_tokens": 300},
        )
        response = model.chat(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract ingredients from the food item image"},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + encoded_image}}
                ]
            }]
        )
        return response['choices'][0]['message']['content']


class FilterIngredientsTool:
    @tool("Filter ingredients")
    def filter_ingredients(raw_ingredients: str) -> List[str]:
        """
        Processes raw ingredient data and filters out non-food items or noise.

        :param raw_ingredients: Raw ingredients as a comma-separated string.
        :return: A list of cleaned and relevant ingredients.
        """
        ingredients = [
            ingredient.strip().lower()
            for ingredient in raw_ingredients.split(',')
            if ingredient.strip()
        ]
        return ingredients


class DietaryFilterTool:
    @tool("Filter based on dietary restrictions")
    def filter_based_on_restrictions(
        ingredients: List[str],
        dietary_restrictions: Optional[str] = None
    ) -> List[str]:
        """
        Uses an LLM to filter ingredients based on dietary restrictions.

        :param ingredients: List of ingredients.
        :param dietary_restrictions: E.g. vegan, gluten-free. Defaults to None.
        :return: Filtered list of compliant ingredients.
        """
        if not dietary_restrictions:
            return ingredients

        model = ModelInference(
            model_id="ibm/granite-4-h-small",
            credentials=credentials,
            project_id=project_id,
            params={"max_tokens": 150},
        )

        prompt = f"""
        You are an AI nutritionist specialized in dietary restrictions.
        Given the following list of ingredients: {', '.join(ingredients)},
        and the dietary restriction: {dietary_restrictions},
        remove any ingredient that does not comply with this restriction.
        Return only the compliant ingredients as a comma-separated list with no additional commentary.
        """

        response = model.chat(
            messages=[{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }]
        )

        filtered = response['choices'][0]['message']['content'].strip().lower()
        return [item.strip() for item in filtered.split(',') if item.strip()]


class NutrientAnalysisTool:
    @tool("Analyze nutritional values and calories of the dish from uploaded image")
    def analyze_image(image_input: str):
        """
        Provide a detailed nutrient breakdown and estimate total calories from an image.

        :param image_input: The image file path (local) or URL (remote).
        :return: Nutrient breakdown and calorie information as a string.
        """
        logging.info("Analyzing nutritional values...")
        encoded_image = _encode_image(image_input)

        model = ModelInference(
            model_id="meta-llama/llama-3-2-90b-vision-instruct",
            credentials=credentials,
            project_id=project_id,
            params={"max_tokens": 300},
        )

        assistant_prompt = """
        You are an expert nutritionist. Analyze the food items in the image and provide:
        1. Identification: List each food item.
        2. Portion Size & Calorie Estimation: For each item, specify portion and calories.
        3. Total Calories: Sum of all items.
        4. Nutrient Breakdown: Protein, Carbohydrates, Fats, Vitamins, Minerals.
        5. Health Evaluation: One paragraph on overall healthiness.
        6. Disclaimer: Note that values are approximate.
        """

        response = model.chat(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": assistant_prompt},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + encoded_image}}
                ]
            }]
        )
        return response['choices'][0]['message']['content']

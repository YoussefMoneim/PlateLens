import os
import yaml
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.tools import (
    ExtractIngredientsTool,
    FilterIngredientsTool,
    DietaryFilterTool,
    NutrientAnalysisTool
)
from ibm_watsonx_ai import Credentials, APIClient
from src.models import RecipeSuggestionOutput, NutrientAnalysisOutput

credentials = Credentials(url="https://us-south.ml.cloud.ibm.com")
client = APIClient(credentials)
project_id = "skills-network"

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


@CrewBase
class BasePlateLensCrew:
    """Base class — shared agents and tasks for all PlateLens crews."""

    agents_config_path = os.path.join(CONFIG_DIR, 'agents.yaml')
    tasks_config_path  = os.path.join(CONFIG_DIR, 'tasks.yaml')

    def __init__(self, image_data: str, dietary_restrictions: str = None):
        self.image_data = image_data
        self.dietary_restrictions = dietary_restrictions

        with open(self.agents_config_path, 'r') as f:
            self.agents_config = yaml.safe_load(f)

        with open(self.tasks_config_path, 'r') as f:
            self.tasks_config = yaml.safe_load(f)

    # ── Agents ───────────────────────────────────────────────────────────────

    @agent
    def ingredient_detection_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['ingredient_detection_agent'],
            tools=[
                ExtractIngredientsTool.extract_ingredient,
                FilterIngredientsTool.filter_ingredients
            ],
            allow_delegation=False,
            verbose=True
        )

    @agent
    def dietary_filtering_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['dietary_filtering_agent'],
            tools=[DietaryFilterTool.filter_based_on_restrictions],
            allow_delegation=True,
            max_iter=6,
            verbose=True
        )

    @agent
    def nutrient_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['nutrient_analysis_agent'],
            tools=[NutrientAnalysisTool.analyze_image],
            allow_delegation=False,
            max_iter=4,
            verbose=True
        )

    @agent
    def recipe_suggestion_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['recipe_suggestion_agent'],
            allow_delegation=False,
            verbose=True
        )

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task
    def ingredient_detection_task(self) -> Task:
        task_config = self.tasks_config['ingredient_detection_task']
        return Task(
            description=task_config['description'],
            agent=self.ingredient_detection_agent(),
            expected_output=task_config['expected_output']
        )

    @task
    def dietary_filtering_task(self) -> Task:
        task_config = self.tasks_config['dietary_filtering_task']
        return Task(
            description=task_config['description'],
            agent=self.dietary_filtering_agent(),
            context=[self.ingredient_detection_task()],  # reads output of ingredient task
            expected_output=task_config['expected_output']
        )

    @task
    def nutrient_analysis_task(self) -> Task:
        task_config = self.tasks_config['nutrient_analysis_task']
        return Task(
            description=task_config['description'],
            agent=self.nutrient_analysis_agent(),
            expected_output=task_config['expected_output'],
            output_pydantic=NutrientAnalysisOutput
        )

    @task
    def recipe_suggestion_task(self) -> Task:
        task_config = self.tasks_config['recipe_suggestion_task']
        return Task(
            description=task_config['description'],
            agent=self.recipe_suggestion_agent(),
            context=[self.dietary_filtering_task()],     # reads filtered ingredients
            expected_output=task_config['expected_output'],
            output_pydantic=RecipeSuggestionOutput
        )


# ── Recipe Crew ───────────────────────────────────────────────────────────────

@CrewBase
class PlateLensRecipeCrew(BasePlateLensCrew):
    """
    Crew for generating recipe suggestions.
    Flow: ingredient_detection → dietary_filtering → recipe_suggestion
    """

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.ingredient_detection_agent(),
                self.dietary_filtering_agent(),
                self.recipe_suggestion_agent()
            ],
            tasks=[
                self.ingredient_detection_task(),
                self.dietary_filtering_task(),
                self.recipe_suggestion_task()
            ],
            process=Process.sequential,
            verbose=True
        )


# ── Analysis Crew ─────────────────────────────────────────────────────────────

@CrewBase
class PlateLensAnalysisCrew(BasePlateLensCrew):
    """
    Crew for nutritional analysis.
    Flow: nutrient_analysis only (single agent, single task)
    """

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.nutrient_analysis_agent()
            ],
            tasks=[
                self.nutrient_analysis_task()
            ],
            process=Process.sequential,
            verbose=True
        )

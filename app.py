import gradio as gr
from src.crew import PlateLensRecipeCrew, PlateLensAnalysisCrew


# ── Output formatters ─────────────────────────────────────────────────────────

def format_recipe_output(final_output: dict) -> str:
    output = "## 🍽 Recipe Ideas\n\n"
    recipes = []

    if "recipes" in final_output:
        recipes = final_output["recipes"]
    else:
        recipe_task_output = final_output.get("recipe_suggestion_task")
        if recipe_task_output and hasattr(recipe_task_output, "json_dict") and recipe_task_output.json_dict:
            recipes = recipe_task_output.json_dict.get("recipes", [])

    if recipes:
        for idx, recipe in enumerate(recipes, 1):
            output += f"### {idx}. {recipe['title']}\n\n"
            output += "**Ingredients:**\n"
            output += "| Ingredient |\n"
            output += "|------------|\n"
            for ingredient in recipe['ingredients']:
                output += f"| {ingredient} |\n"
            output += "\n"
            output += f"**Instructions:**\n{recipe['instructions']}\n\n"
            output += f"**Calorie Estimate:** {recipe['calorie_estimate']} kcal\n\n"
            output += "---\n\n"
    else:
        output += "No recipes could be generated."

    return output


def format_analysis_output(final_output: dict) -> str:
    output = "## 🥗 Nutritional Analysis\n\n"

    if dish := final_output.get('dish'):
        output += f"**Dish:** {dish}\n\n"
    if portion := final_output.get('portion_size'):
        output += f"**Portion Size:** {portion}\n\n"
    if est_cal := final_output.get('estimated_calories'):
        output += f"**Estimated Calories:** {est_cal} calories\n\n"
    if total_cal := final_output.get('total_calories'):
        output += f"**Total Calories:** {total_cal} calories\n\n"

    output += "**Nutrient Breakdown:**\n\n"
    output += "| **Nutrient**       | **Amount** |\n"
    output += "|--------------------|------------|\n"

    nutrients = final_output.get('nutrients', {})
    for macro in ['protein', 'carbohydrates', 'fats']:
        if value := nutrients.get(macro):
            output += f"| **{macro.capitalize()}** | {value} |\n"

    vitamins = nutrients.get('vitamins', [])
    if vitamins:
        output += "\n**Vitamins:**\n\n"
        output += "| **Vitamin** | **%DV** |\n"
        output += "|-------------|--------|\n"
        for v in vitamins:
            output += f"| {v.get('name','N/A')} | {v.get('percentage_dv','N/A')} |\n"

    minerals = nutrients.get('minerals', [])
    if minerals:
        output += "\n**Minerals:**\n\n"
        output += "| **Mineral** | **Amount** |\n"
        output += "|-------------|-----------|\n"
        for m in minerals:
            output += f"| {m.get('name','N/A')} | {m.get('amount','N/A')} |\n"

    if health_eval := final_output.get('health_evaluation'):
        output += "\n**Health Evaluation:**\n\n"
        output += health_eval + "\n"

    return output


# ── Main handler ──────────────────────────────────────────────────────────────

def analyze_food(image, dietary_restrictions, workflow_type, progress=gr.Progress(track_tqdm=True)):
    """Main Gradio handler — routes to the appropriate crew based on workflow type."""

    image.save("uploaded_image.jpg")
    image_path = "uploaded_image.jpg"

    inputs = {
        'uploaded_image':       image_path,
        'dietary_restrictions': dietary_restrictions,
        'workflow_type':        workflow_type
    }

    if workflow_type == "recipe":
        crew_instance = PlateLensRecipeCrew(
            image_data=image_path,
            dietary_restrictions=dietary_restrictions
        )
    elif workflow_type == "analysis":
        crew_instance = PlateLensAnalysisCrew(image_data=image_path)
    else:
        return "Invalid workflow type. Choose 'recipe' or 'analysis'."

    crew_obj   = crew_instance.crew()
    final_output = crew_obj.kickoff(inputs=inputs).to_dict()

    if workflow_type == "recipe":
        return format_recipe_output(final_output)
    elif workflow_type == "analysis":
        return format_analysis_output(final_output)


# ── Gradio UI ─────────────────────────────────────────────────────────────────

css = """
.title { font-size: 1.5em !important; text-align: center !important; color: #FFD700; }
.text  { text-align: center; }
"""

js = """
function createGradioAnimation() {
    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.style.fontSize = '2em';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    container.style.marginBottom = '20px';
    container.style.color = '#eba93f';

    var text = 'Welcome to PlateLens!';
    for (var i = 0; i < text.length; i++) {
        (function(i){
            setTimeout(function(){
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.1s';
                letter.innerText = text[i];
                container.appendChild(letter);
                setTimeout(function() { letter.style.opacity = '0.9'; }, 50);
            }, i * 250);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    gradioContainer.insertBefore(container, gradioContainer.firstChild);
    return 'Animation created';
}
"""

with gr.Blocks(theme=gr.themes.Citrus(), css=css, js=js) as demo:
    gr.Markdown("# 🍽 PlateLens — AI Nutrition Assistant", elem_classes="title")
    gr.Markdown("Upload an image of your fridge content, enter your dietary restriction and select **recipe** to get recipe ideas.", elem_classes="text")
    gr.Markdown("Upload an image of a complete dish and select **analysis** to get a full nutritional breakdown.", elem_classes="text")

    with gr.Row():
        with gr.Column(scale=1, min_width=400):
            gr.Markdown("## Inputs", elem_classes="title")
            image_input    = gr.Image(type="pil", label="Upload Image")
            dietary_input  = gr.Textbox(label="Dietary Restrictions (optional)", placeholder="e.g., vegan, keto, gluten-free")
            workflow_radio = gr.Radio(["recipe", "analysis"], label="Workflow Type")
            submit_btn     = gr.Button("Analyze 🔍")

        with gr.Column(scale=2, min_width=600):
            gr.Examples(
                examples=[
                    ["examples/food-1.jpg", "vegan",   "recipe"],
                    ["examples/food-2.jpg", "",        "analysis"],
                    ["examples/food-3.jpg", "keto",    "recipe"],
                    ["examples/food-4.jpg", "",        "analysis"],
                ],
                inputs=[image_input, dietary_input, workflow_radio],
                label="Try an Example — select one then click Analyze"
            )
            gr.Markdown("## Results", elem_classes="title")
            result_display = gr.Markdown(
                "<div style='border:1px solid #ccc;padding:1rem;text-align:center;color:#666;'>No results yet</div>",
                height=500
            )

    submit_btn.click(
        fn=analyze_food,
        inputs=[image_input, dietary_input, workflow_radio],
        outputs=result_display
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=5000)

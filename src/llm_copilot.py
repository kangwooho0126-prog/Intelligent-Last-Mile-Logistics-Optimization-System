import json
from pathlib import Path
from urllib import request

from pyparsing import line

from src.prompts import build_dispatch_analysis_prompt


def load_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_template_analysis(comparison_text: str) -> str:
    lines = [line.strip() for line in comparison_text.splitlines() if line.strip()]

    data = {}
    for line in lines:
        if ":" in line:
           parts = line.split(":", 1)
           if len(parts) == 2 and parts[1].strip() != "":
              key, value = parts
              data[key.strip()] = value.strip()

    baseline_distance = data.get("Baseline total distance", "N/A")
    ortools_distance = data.get("OR-Tools total distance", "N/A")
    distance_reduction = data.get("Distance reduction", "N/A")

    baseline_cost = data.get("Baseline total cost", "N/A")
    ortools_cost = data.get("OR-Tools total cost", "N/A")
    cost_reduction = data.get("Cost reduction", "N/A")

    baseline_vehicles = data.get("Baseline vehicles used", "N/A")
    ortools_vehicles = data.get("OR-Tools vehicles used", "N/A")

    baseline_util = data.get("Baseline average load utilization", "N/A")
    ortools_util = data.get("OR-Tools average load utilization", "N/A")

    analysis = f"""
The OR-Tools solution outperformed the greedy baseline in the last-mile routing experiment.

Compared with the baseline, the optimized solution reduced total travel distance from {baseline_distance} to {ortools_distance}, representing a distance reduction of {distance_reduction}. Total delivery cost also decreased from {baseline_cost} to {ortools_cost}, corresponding to a cost reduction of {cost_reduction}.

Both methods used the same number of vehicles ({baseline_vehicles} vs. {ortools_vehicles}), while average load utilization remained stable ({baseline_util} vs. {ortools_util}). This indicates that the performance gain was achieved mainly through better route structuring and more efficient node sequencing, rather than by increasing logistics resources.

From a business perspective, the result shows that optimization-based routing can significantly improve delivery efficiency and reduce operating cost under the same fleet setting, which is highly relevant for urban last-mile parcel distribution.
""".strip()

    return analysis


def call_openai_compatible_api(
    prompt: str,
    api_key: str,
    base_url: str,
    model_name: str
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a professional logistics optimization analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    data = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    with request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    return result["choices"][0]["message"]["content"].strip()


def generate_dispatch_analysis(
    comparison_summary_path: str,
    mode: str = "template",
    api_key: str = "",
    base_url: str = "",
    model_name: str = ""
) -> str:
    comparison_text = load_text_file(comparison_summary_path)

    if mode == "template":
        return generate_template_analysis(comparison_text)

    if mode == "api":
        if not api_key or not base_url or not model_name:
            raise ValueError("API mode requires api_key, base_url, and model_name.")
        prompt = build_dispatch_analysis_prompt(comparison_text)
        return call_openai_compatible_api(
            prompt=prompt,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name
        )

    raise ValueError("mode must be either 'template' or 'api'.")


def save_analysis_text(analysis_text: str, save_path: str) -> None:
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(analysis_text)
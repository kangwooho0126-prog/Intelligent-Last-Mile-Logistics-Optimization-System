def build_dispatch_analysis_prompt(comparison_text: str) -> str:
    return f"""
You are a logistics optimization analyst.

Based on the routing experiment results below, write a concise business-style analysis.

Requirements:
1. Summarize which method performs better.
2. Explain the improvements in total distance, delivery cost, vehicle usage, and load utilization.
3. Highlight that the gains come from route optimization rather than adding more vehicles.
4. Keep the tone professional and suitable for a supply chain algorithm engineering project.
5. Output in English.

Experiment results:
{comparison_text}
""".strip()
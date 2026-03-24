from pathlib import Path

PROJECT_STRUCTURE = {
    "data": {
        "raw": {},
        "processed": {}
    },
    "results": {
        "base": {},
        "scenarios": {},
        "plots": {}
    },
    "src": {
        "__init__.py": None,
        "config.py": None,
        "data_loader.py": None,
        "scenario_builder.py": None,
        "distance_utils.py": None,
        "baseline_solver.py": None,
        "ortools_solver.py": None,
        "evaluator.py": None,
        "visualization.py": None,
        "scenario_manager.py": None,
        "llm_copilot.py": None,
        "agent_dispatcher.py": None,
        "prompts.py": None
    },
    "app": {
        "streamlit_app.py": None
    },
    "notebooks": {
        "quick_demo.ipynb": None
    },
    "main.py": None,
    "requirements.txt": None,
    "README.md": None
}


def create_structure(base_path: Path, structure: dict) -> None:
    for name, content in structure.items():
        current_path = base_path / name

        if content is None:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.touch(exist_ok=True)
        elif isinstance(content, dict):
            current_path.mkdir(parents=True, exist_ok=True)
            create_structure(current_path, content)


def write_initial_files(base_path: Path) -> None:
    readme_path = base_path / "README.md"
    requirements_path = base_path / "requirements.txt"
    main_path = base_path / "main.py"

    if readme_path.exists() and readme_path.stat().st_size == 0:
        readme_path.write_text(
            "# Intelligent Last-Mile Logistics Optimization System\n\n"
            "This project focuses on CVRP-based last-mile logistics optimization, "
            "with LLM and lightweight agent modules for explanation and scenario-based decision support.\n",
            encoding="utf-8"
        )

    if requirements_path.exists() and requirements_path.stat().st_size == 0:
        requirements_path.write_text(
            "pandas\n"
            "numpy\n"
            "matplotlib\n"
            "ortools\n"
            "streamlit\n",
            encoding="utf-8"
        )

    if main_path.exists() and main_path.stat().st_size == 0:
        main_path.write_text(
            "def main():\n"
            "    print('Project structure initialized successfully.')\n\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n",
            encoding="utf-8"
        )


if __name__ == "__main__":
    base_dir = Path.cwd()
    create_structure(base_dir, PROJECT_STRUCTURE)
    write_initial_files(base_dir)
    print(f"Project structure created under: {base_dir}")
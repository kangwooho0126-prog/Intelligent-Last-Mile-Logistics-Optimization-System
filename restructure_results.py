import os
import shutil

BASE_DIR = os.getcwd()
RESULTS_DIR = os.path.join(BASE_DIR, "results")

TARGET_DATASET = "A-n32-k5_cvprtw_medium"  # 你当前主要实验

BASE_FOLDER = os.path.join(RESULTS_DIR, "base")
PLOTS_FOLDER = os.path.join(RESULTS_DIR, "plots")
TARGET_FOLDER = os.path.join(RESULTS_DIR, TARGET_DATASET)

def move_base_files():
    if not os.path.exists(BASE_FOLDER):
        return

    for file in os.listdir(BASE_FOLDER):
        src = os.path.join(BASE_FOLDER, file)
        dst = os.path.join(TARGET_FOLDER, file)

        print(f"Moving {file} → {TARGET_DATASET}/")
        shutil.move(src, dst)

def move_plots():
    if not os.path.exists(PLOTS_FOLDER):
        return

    target_plot_dir = os.path.join(TARGET_FOLDER, "plots")
    os.makedirs(target_plot_dir, exist_ok=True)

    for file in os.listdir(PLOTS_FOLDER):
        src = os.path.join(PLOTS_FOLDER, file)
        dst = os.path.join(target_plot_dir, file)

        print(f"Moving plot {file} → {TARGET_DATASET}/plots/")
        shutil.move(src, dst)

def clean_empty_dirs():
    for folder in ["base", "plots"]:
        path = os.path.join(RESULTS_DIR, folder)
        if os.path.exists(path) and not os.listdir(path):
            print(f"Removing empty folder: {folder}")
            os.rmdir(path)

def main():
    print("📦 Restructuring results...\n")
    move_base_files()
    move_plots()
    clean_empty_dirs()
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
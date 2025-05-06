import json
import matplotlib.pyplot as plt
import os
from shared.theme import THEME

def fetch_initial_plots(connection):
    try:
        connection.send("get_initial_plots", {})
        json_str = connection.receive_json()
        if not json_str:
            raise ValueError("No data received from the server.")
        plots_data = json.loads(json_str)

        output_dir = "plots"
        os.makedirs(output_dir, exist_ok=True)
        image_paths = []

        # Theme colors
        bg = THEME["bg"]
        fg = THEME["fg"]
        accent = THEME["accent"]
        card_bg = THEME["card_bg"]

        # Plot 1: Histogram of Age
        if "age_hist" in plots_data:
            age_hist = plots_data["age_hist"]
            plt.figure(figsize=(8, 5), facecolor=bg)
            plt.bar(age_hist["bins"], age_hist["counts"], width=5.0, color=accent, edgecolor=fg)
            plt.title("Leeftijdsverdeling van arrestaties", fontsize=16, color=accent)
            plt.xlabel("Leeftijd", fontsize=13, color=fg)
            plt.ylabel("Aantal arrestaties", fontsize=13, color=fg)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.gca().set_facecolor(card_bg)
            plt.xticks(color=fg)
            plt.yticks(color=fg)
            plt.tight_layout()
            file_path = os.path.join(output_dir, "age_hist.png")
            plt.savefig(file_path, facecolor=bg)
            image_paths.append(file_path)
            plt.close()

        # Plot 2: Arrests Over Time
        if "arrests_over_time" in plots_data:
            arrests_over_time = plots_data["arrests_over_time"]
            plt.figure(figsize=(10, 5), facecolor=bg)
            plt.plot(arrests_over_time["months"], arrests_over_time["counts"], marker='o', color=accent, label="Arrestaties")
            plt.title("Arrestaties per maand", fontsize=16, color=accent)
            plt.xlabel("Maand", fontsize=13, color=fg)
            plt.ylabel("Aantal arrestaties", fontsize=13, color=fg)
            plt.xticks(rotation=45, color=fg)
            plt.yticks(color=fg)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.gca().set_facecolor(card_bg)
            plt.legend(facecolor=card_bg, edgecolor=fg, labelcolor=fg)
            plt.tight_layout()
            file_path = os.path.join(output_dir, "arrests_over_time.png")
            plt.savefig(file_path, facecolor=bg)
            image_paths.append(file_path)
            plt.close()

        # Plot 3: Arrests by Gender
        if "gender_count" in plots_data:
            gender_count = plots_data["gender_count"]
            plt.figure(figsize=(6, 5), facecolor=bg)
            bars = plt.bar(gender_count["categories"], gender_count["counts"], color=accent, edgecolor=fg)
            plt.title("Arrestaties per geslacht", fontsize=16, color=accent)
            plt.xlabel("Geslacht", fontsize=13, color=fg)
            plt.ylabel("Aantal arrestaties", fontsize=13, color=fg)
            plt.gca().set_facecolor(card_bg)
            plt.xticks(color=fg)
            plt.yticks(color=fg)
            for bar in bars:
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', color=fg, fontsize=11)
            plt.tight_layout()
            file_path = os.path.join(output_dir, "gender_count.png")
            plt.savefig(file_path, facecolor=bg)
            image_paths.append(file_path)
            plt.close()

        # Plot 4: Arrests by Area (Top 5)
        if "area_count" in plots_data:
            area_count = plots_data["area_count"]
            plt.figure(figsize=(7, 5), facecolor=bg)
            bars = plt.bar(area_count["areas"], area_count["counts"], color=accent, edgecolor=fg)
            plt.title("Top 5 gebieden met meeste arrestaties", fontsize=16, color=accent)
            plt.xlabel("Gebied", fontsize=13, color=fg)
            plt.ylabel("Aantal arrestaties", fontsize=13, color=fg)
            plt.gca().set_facecolor(card_bg)
            plt.xticks(color=fg)
            plt.yticks(color=fg)
            for bar in bars:
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', color=fg, fontsize=11)
            plt.tight_layout()
            file_path = os.path.join(output_dir, "area_count.png")
            plt.savefig(file_path, facecolor=bg)
            image_paths.append(file_path)
            plt.close()

        # Plot 5: Top 5 Most Common Crimes
        if "top_crimes" in plots_data:
            top_crimes = plots_data["top_crimes"]
            plt.figure(figsize=(10, 5), facecolor=bg)
            bars = plt.barh(top_crimes["crimes"], top_crimes["counts"], color=accent, edgecolor=fg)
            plt.title("Top 5 meest voorkomende misdrijven", fontsize=16, color=accent)
            plt.xlabel("Aantal arrestaties", fontsize=13, color=fg)
            plt.ylabel("Misdrijf", fontsize=13, color=fg)
            plt.gca().set_facecolor(card_bg)
            plt.xticks(color=fg)
            plt.yticks(color=fg)
            for bar in bars:
                plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f"{int(bar.get_width())}", va='center', color=fg, fontsize=11)
            plt.tight_layout()
            file_path = os.path.join(output_dir, "top_crimes.png")
            plt.savefig(file_path, facecolor=bg)
            image_paths.append(file_path)
            plt.close()

        return plots_data.get("summary", {}), image_paths

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to decode JSON: {e}")
        return {}, []
    except Exception as e:
        print(f"[ERROR] Failed to fetch or generate plot images: {e}")
        return {}, []
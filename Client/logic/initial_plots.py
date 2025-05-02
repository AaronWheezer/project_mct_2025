import json
import matplotlib.pyplot as plt
import seaborn as sns
import os

def fetch_initial_plots(connection):
    try:
        # Send request to server for initial plots
        connection.send("get_initial_plots", {})

        # Receive the JSON data using a length-prefixed protocol
        json_str = connection.receive_json()
        print(f"[DEBUG] Received JSON string: {json_str}")
        if not json_str:
            raise ValueError("No data received from the server.")
        plots_data = json.loads(json_str)
        print(f"[DEBUG] Received plot data: {plots_data}")

        # Create a directory for saving plots if it doesn't exist
        output_dir = "plots"
        os.makedirs(output_dir, exist_ok=True)

        # Generate the plots locally and save them as image files
        image_paths = []

        # Plot 1: Histogram of Age
        if "age_hist" in plots_data:
            age_hist = plots_data["age_hist"]
            plt.figure(figsize=(8, 6))
            plt.bar(age_hist["bins"], age_hist["counts"], width=5.0)
            plt.title("Histogram of Age")
            plt.xlabel("Age")
            plt.ylabel("Frequency")
            plt.tight_layout()
            file_path = os.path.join(output_dir, "age_hist.png")
            plt.savefig(file_path)
            image_paths.append(file_path)
            plt.close()

        # Plot 2: Arrests Over Time
        if "arrests_over_time" in plots_data:
            arrests_over_time = plots_data["arrests_over_time"]
            plt.figure(figsize=(12, 6))
            plt.plot(arrests_over_time["months"], arrests_over_time["counts"], marker='o')
            plt.title("Arrests Over Time (Monthly)")
            plt.xlabel("Month")
            plt.ylabel("Number of Arrests")
            plt.xticks(rotation=45)
            plt.tight_layout()
            file_path = os.path.join(output_dir, "arrests_over_time.png")
            plt.savefig(file_path)
            image_paths.append(file_path)
            plt.close()

        # Plot 3: Countplot by Gender
        if "gender_count" in plots_data:
            gender_count = plots_data["gender_count"]
            plt.figure(figsize=(6, 6))
            plt.bar(gender_count["categories"], gender_count["counts"])
            plt.title("Arrests by Gender")
            plt.xlabel("Gender")
            plt.ylabel("Count")
            plt.tight_layout()
            file_path = os.path.join(output_dir, "gender_count.png")
            plt.savefig(file_path)
            image_paths.append(file_path)
            plt.close()

        # Plot 4: Boxplot of Age by Descent Code
        if "age_box_descent" in plots_data:
            age_box_descent = plots_data["age_box_descent"]
            categories = age_box_descent["categories"]
            summary = age_box_descent["summary"]
            plt.figure(figsize=(10, 6))
            for category in categories:
                stats = summary[category]
                plt.boxplot(
                    [[stats["min"], stats["q1"], stats["median"], stats["q3"], stats["max"]]],
                    positions=[categories.index(category)],
                    labels=[category]
                )
            plt.title("Boxplot of Age by Descent Code")
            plt.xlabel("Descent Code")
            plt.ylabel("Age")
            plt.tight_layout()
            file_path = os.path.join(output_dir, "age_box_descent.png")
            plt.savefig(file_path)
            image_paths.append(file_path)
            plt.close()

        return image_paths

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to decode JSON: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to fetch or generate plot images: {e}")
        return []
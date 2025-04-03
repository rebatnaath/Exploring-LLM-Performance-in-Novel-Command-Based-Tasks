import os
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import random
import numpy as np  # Required for grouped bar chart

# Mapping of country names to ISO codes
COUNTRY_TO_ISO = {
    "Germany": "DE",
    "Sweden": "SE",
    "Brazil": "BR",
    "Nepal": "NP",
    "Zambia": "ZM",
    "Australia": "AU",
    "Bhutan": "BT",
    "Saudi Arabia": "SA",
    "Kazakhstan": "KZ",
    "Tanzania": "TZ"
}

class FlagRatingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flag Rating Application")
        self.root.geometry("1000x700")  # Larger window for side-by-side display
        
        # Data structures to store paths and ratings
        self.ai_folders = []
        self.flag_paths = []
        self.current_index = 0
        self.ratings = {}
        self.actual_flags_dir = "actual-flags"
        
        # Find all AI folders and flag images
        self.find_flag_images()
        
        # Shuffle the flag paths to randomize the order
        random.shuffle(self.flag_paths)
        
        # Create UI elements
        self.setup_ui()
        
        # Start showing flags
        if self.flag_paths:
            self.show_current_flag()
        else:
            self.info_label.config(text="No flag images found!")
    
    def find_flag_images(self):
        # Get all directories in the root that might be AI model folders
        potential_ai_folders = [d for d in os.listdir() if os.path.isdir(d) and 
                               d not in ['.git', '__pycache__', self.actual_flags_dir]]
        
        for ai_folder in potential_ai_folders:
            # Check if this folder contains flag subfolders
            subfolders = [d for d in os.listdir(ai_folder) if os.path.isdir(os.path.join(ai_folder, d)) and 'flags' in d.lower()]
            
            if subfolders:
                self.ai_folders.append(ai_folder)
                
                # For each subfolder, find all PNG files
                for subfolder in subfolders:
                    subfolder_path = os.path.join(ai_folder, subfolder)
                    flag_files = [f for f in os.listdir(subfolder_path) if f.endswith('.png')]
                    
                    for flag_file in flag_files:
                        flag_path = os.path.join(ai_folder, subfolder, flag_file)
                        country_name = os.path.splitext(flag_file)[0]
                        
                        # Only include flags that have a corresponding actual flag
                        if country_name in COUNTRY_TO_ISO:
                            self.flag_paths.append({
                                'path': flag_path,
                                'ai_folder': ai_folder,
                                'subfolder': subfolder,
                                'country': country_name,
                                'iso_code': COUNTRY_TO_ISO[country_name]
                            })
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Flag Comparison and Rating", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame for displaying flags side by side
        self.flags_frame = ttk.Frame(main_frame)
        self.flags_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Actual flag
        self.actual_flag_frame = ttk.LabelFrame(self.flags_frame, text="Actual Flag")
        self.actual_flag_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.actual_flag_label = ttk.Label(self.actual_flag_frame)
        self.actual_flag_label.pack(padx=10, pady=10, expand=True)
        
        # Right side - AI-generated flag
        self.ai_flag_frame = ttk.LabelFrame(self.flags_frame, text="AI-Generated Flag")
        self.ai_flag_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.ai_flag_label = ttk.Label(self.ai_flag_frame)
        self.ai_flag_label.pack(padx=10, pady=10, expand=True)
        
        # Configure grid weights
        self.flags_frame.columnconfigure(0, weight=1)
        self.flags_frame.columnconfigure(1, weight=1)
        self.flags_frame.rowconfigure(0, weight=1)
        
        # Info label for country name
        self.info_label = ttk.Label(main_frame, font=("Arial", 14))
        self.info_label.pack(pady=10)
        
        # Frame for rating buttons
        rating_frame = ttk.Frame(main_frame)
        rating_frame.pack(pady=10)
        
        rating_label = ttk.Label(rating_frame, text="Rate similarity (1-10):", font=("Arial", 12))
        rating_label.grid(row=0, column=0, columnspan=10, pady=(0, 10))
        
        # Create rating buttons (1-10)
        for i in range(1, 11):
            btn = ttk.Button(rating_frame, text=str(i), width=5,
                            command=lambda score=i: self.rate_flag(score))
            btn.grid(row=1, column=i-1, padx=5)
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.pack(pady=10)
    
    def show_current_flag(self):
        if 0 <= self.current_index < len(self.flag_paths):
            flag_info = self.flag_paths[self.current_index]
            
            # Update progress label
            self.progress_label.config(
                text=f"Progress: {self.current_index + 1}/{len(self.flag_paths)}"
            )
            
            # Display country name
            self.info_label.config(
                text=f"Country: {flag_info['country']}"
            )
            
            # Load and display the actual flag
            actual_flag_path = os.path.join(self.actual_flags_dir, f"{flag_info['iso_code']}.png")
            if os.path.exists(actual_flag_path):
                self.load_and_display_image(actual_flag_path, self.actual_flag_label)
            else:
                self.actual_flag_label.config(image=None, text=f"Actual flag not found")
            
            # Load and display the AI-generated flag
            self.load_and_display_image(flag_info['path'], self.ai_flag_label)
    
    def load_and_display_image(self, image_path, label_widget):
        try:
            img = Image.open(image_path)
            # Resize image if needed while maintaining aspect ratio
            width, height = img.size
            max_size = 300
            if width > max_size or height > max_size:
                ratio = min(max_size/width, max_size/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            label_widget.config(image=photo)
            label_widget.image = photo  # Keep a reference
        except Exception as e:
            label_widget.config(image=None, text=f"Error loading image: {e}")
    
    def rate_flag(self, score):
        if 0 <= self.current_index < len(self.flag_paths):
            flag_info = self.flag_paths[self.current_index]
            key = (flag_info['ai_folder'], flag_info['subfolder'], flag_info['country'])
            self.ratings[key] = score
            
            # Move to the next flag
            self.current_index += 1
            
            if self.current_index < len(self.flag_paths):
                self.show_current_flag()
            else:
                self.finish_rating()
    
    def finish_rating(self):
        # Clear the display
        self.actual_flag_label.config(image=None)
        self.ai_flag_label.config(image=None)
        self.info_label.config(text="Rating completed! Generating results...")
        
        # Calculate averages and generate JSON
        results = self.calculate_averages()
        
        # Save results to JSON file
        with open('flag_ratings.json', 'w') as f:
            json.dump(results, f, indent=4)
        
        # Show completion message
        self.info_label.config(text="Ratings saved to flag_ratings.json")
        
        # Generate and display charts
        self.generate_charts(results)
    
    def calculate_averages(self):
        results = {
            "overall_average": 0,
            "ai_folders": {}
        }
        
        total_score = 0
        total_count = 0
        
        # Group ratings by AI folder and subfolder
        for (ai_folder, subfolder, country), score in self.ratings.items():
            # Initialize AI folder if not exists
            if ai_folder not in results["ai_folders"]:
                results["ai_folders"][ai_folder] = {
                    "average": 0,
                    "subfolders": {}
                }
            
            # Initialize subfolder if not exists
            if subfolder not in results["ai_folders"][ai_folder]["subfolders"]:
                results["ai_folders"][ai_folder]["subfolders"][subfolder] = {
                    "average": 0,
                    "flags": {}
                }
            
            # Add flag rating
            results["ai_folders"][ai_folder]["subfolders"][subfolder]["flags"][country] = score
            
            # Update totals
            total_score += score
            total_count += 1
        
        # Calculate averages for each subfolder
        for ai_folder in results["ai_folders"]:
            ai_total = 0
            ai_count = 0
            
            for subfolder in results["ai_folders"][ai_folder]["subfolders"]:
                subfolder_data = results["ai_folders"][ai_folder]["subfolders"][subfolder]
                subfolder_total = sum(subfolder_data["flags"].values())
                subfolder_count = len(subfolder_data["flags"])
                
                if subfolder_count > 0:
                    subfolder_data["average"] = round(subfolder_total / subfolder_count, 2)
                    ai_total += subfolder_total
                    ai_count += subfolder_count
            
            # Calculate average for AI folder
            if ai_count > 0:
                results["ai_folders"][ai_folder]["average"] = round(ai_total / ai_count, 2)
        
        # Calculate overall average
        if total_count > 0:
            results["overall_average"] = round(total_score / total_count, 2)
        
        return results
    
    def generate_charts(self, results):
        # Create a new window for charts
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Rating Results")
        chart_window.geometry("1000x700")
        
        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(chart_window)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tab for AI folder comparison
        ai_tab = ttk.Frame(notebook)
        notebook.add(ai_tab, text="AI Models Comparison")
        
        # Create figure for AI comparison
        ai_fig = plt.Figure(figsize=(10, 6))
        ai_ax = ai_fig.add_subplot(111)
        
        # Extract AI folder averages
        ai_names = list(results["ai_folders"].keys())
        ai_scores = [results["ai_folders"][ai]["average"] for ai in ai_names]
        
        # Sort by score for better visualization
        sorted_data = sorted(zip(ai_names, ai_scores), key=lambda x: x[1], reverse=True)
        sorted_ai_names, sorted_ai_scores = zip(*sorted_data) if sorted_data else ([], [])
        
        # Create bar chart
        bars = ai_ax.bar(sorted_ai_names, sorted_ai_scores)
        ai_ax.set_ylim(0, 10)
        ai_ax.set_title("Average Similarity Scores by AI Model")
        ai_ax.set_ylabel("Average Score")
        ai_ax.set_xlabel("AI Model")
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ai_ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # Add the figure to the tab
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(ai_fig, ai_tab)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each AI folder to show subfolder comparisons
        for ai_folder in results["ai_folders"]:
            ai_detail_tab = ttk.Frame(notebook)
            notebook.add(ai_detail_tab, text=ai_folder)
            
            # Create figure for subfolder comparison
            subfolder_fig = plt.Figure(figsize=(10, 6))
            subfolder_ax = subfolder_fig.add_subplot(111)
            
            # Extract subfolder averages
            subfolder_names = list(results["ai_folders"][ai_folder]["subfolders"].keys())
            subfolder_scores = [results["ai_folders"][ai_folder]["subfolders"][sf]["average"] 
                              for sf in subfolder_names]
            
            # Sort by score
            sorted_data = sorted(zip(subfolder_names, subfolder_scores), key=lambda x: x[1], reverse=True)
            sorted_subfolder_names, sorted_subfolder_scores = zip(*sorted_data) if sorted_data else ([], [])
            
            # Create bar chart
            bars = subfolder_ax.bar(sorted_subfolder_names, sorted_subfolder_scores)
            subfolder_ax.set_ylim(0, 10)
            subfolder_ax.set_title(f"Average Similarity Scores for {ai_folder} Subfolders")
            subfolder_ax.set_ylabel("Average Score")
            subfolder_ax.set_xlabel("Subfolder")
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                subfolder_ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.2f}', ha='center', va='bottom')
            
            # Add the figure to the tab
            canvas = FigureCanvasTkAgg(subfolder_fig, ai_detail_tab)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Create a tab for detailed flag scores in this AI folder
            flag_detail_tab = ttk.Frame(notebook)
            notebook.add(flag_detail_tab, text=f"{ai_folder} - Flag Details")
            
            # Create a figure for flag comparison
            flag_fig = plt.Figure(figsize=(12, 6))
            flag_ax = flag_fig.add_subplot(111)
            
            # Collect all flag scores across subfolders
            flag_data = {}
            for subfolder in results["ai_folders"][ai_folder]["subfolders"]:
                for country, score in results["ai_folders"][ai_folder]["subfolders"][subfolder]["flags"].items():
                    if country not in flag_data:
                        flag_data[country] = []
                    flag_data[country].append((subfolder, score))
            
            # Prepare data for grouped bar chart
            countries = list(flag_data.keys())
            subfolders = sorted(set(subfolder for country_data in flag_data.values() 
                                  for subfolder, _ in country_data))
            
            # Create a grouped bar chart
            x = np.arange(len(countries))
            width = 0.8 / len(subfolders)
            
            for i, subfolder in enumerate(subfolders):
                scores = []
                for country in countries:
                    score = next((score for sf, score in flag_data[country] if sf == subfolder), 0)
                    scores.append(score)
                
                offset = width * i - width * (len(subfolders) - 1) / 2
                bars = flag_ax.bar(x + offset, scores, width, label=subfolder)
                
                # Add value labels
                for j, bar in enumerate(bars):
                    if scores[j] > 0:  # Only add label if there's a score
                        height = bar.get_height()
                        flag_ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{height:.1f}', ha='center', va='bottom', fontsize=8)
            
            flag_ax.set_ylim(0, 10)
            flag_ax.set_title(f"Flag Scores for {ai_folder}")
            flag_ax.set_ylabel("Score")
            flag_ax.set_xticks(x)
            flag_ax.set_xticklabels(countries)
            flag_ax.legend(title="Subfolder")
            
            # Add the figure to the tab
            canvas = FigureCanvasTkAgg(flag_fig, flag_detail_tab)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FlagRatingApp(root)
    root.mainloop()
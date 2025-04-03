import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

class FlagEfficiencyAnalyzer:
    def __init__(self):
        self.ai_folders = []
        self.json_files = []
        self.grid_size = (30, 50)  # 30 rows x 50 columns
        self.results = {}
        
    def find_json_files(self):
        """Find all JSON files containing flag commands in the AI model folders."""
        # Get all directories in the root that might be AI model folders
        potential_ai_folders = [d for d in os.listdir() if os.path.isdir(d) and 
                               d not in ['.git', '__pycache__', 'actual-flags']]
        
        for ai_folder in potential_ai_folders:
            # Check if this folder contains flag subfolders
            subfolders = [d for d in os.listdir(ai_folder) if os.path.isdir(os.path.join(ai_folder, d)) and 'flags' in d.lower()]
            
            if subfolders:
                self.ai_folders.append(ai_folder)
                
                # For each subfolder, find the JSON file
                for subfolder in subfolders:
                    subfolder_path = os.path.join(ai_folder, subfolder)
                    
                    # Determine the JSON file name based on the subfolder
                    if subfolder == 'flags':
                        json_filename = f"{ai_folder}-flags-cmd.json"
                    else:
                        json_filename = "cmd.json"
                    
                    json_path = os.path.join(subfolder_path, json_filename)
                    
                    if os.path.exists(json_path):
                        self.json_files.append({
                            'path': json_path,
                            'ai_folder': ai_folder,
                            'subfolder': subfolder
                        })
    
    def parse_command(self, command):
        """Parse a single command and return the affected cells and color."""
        # Background command
        if command.startswith('bg:'):
            color = command[3:]
            # All cells in the grid
            cells = [(row, col) for row in range(1, self.grid_size[0] + 1) 
                              for col in range(self.grid_size[1])]
            return cells, color
        
        # Split command into cells and color
        parts = command.split(':')
        if len(parts) != 2:
            return [], ''
        
        cells_str, color = parts
        affected_cells = []
        
        # Handle range command (e.g., A1-D5:#00FF00)
        if '-' in cells_str and ',' not in cells_str:
            start, end = cells_str.split('-')
            start_col, start_row = self.parse_cell(start)
            end_col, end_row = self.parse_cell(end)
            
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    affected_cells.append((row, col))
        
        # Handle individual cells (e.g., A1,B1,C1:#0000FF)
        elif ',' in cells_str:
            for cell in cells_str.split(','):
                col, row = self.parse_cell(cell)
                affected_cells.append((row, col))
        
        # Handle single cell
        else:
            col, row = self.parse_cell(cells_str)
            affected_cells.append((row, col))
        
        return affected_cells, color
    
    def parse_cell(self, cell):
        """Parse a cell reference (e.g., 'A1') into column and row indices."""
        # Extract column letter and row number
        match = re.match(r'([A-Za-x])(\d+)', cell)
        if not match:
            return -1, -1
        
        col_letter, row_num = match.groups()
        
        # Convert column letter to index (0-49)
        if 'A' <= col_letter <= 'Z':
            col_index = ord(col_letter) - ord('A')
        else:  # lowercase a-x
            col_index = ord(col_letter) - ord('a') + 26
        
        # Convert row number to index (1-30)
        row_index = int(row_num)
        
        return col_index, row_index
    
    def analyze_json_file(self, json_info):
        """Analyze a JSON file for flag efficiency metrics."""
        try:
            with open(json_info['path'], 'r') as f:
                data = json.load(f)
            
            flags_data = data.get('flags', [])
            results = {
                'ai_folder': json_info['ai_folder'],
                'subfolder': json_info['subfolder'],
                'flags': {}
            }
            
            for flag in flags_data:
                country = flag.get('title', '')
                commands = flag.get('commands', [])
                
                # Initialize a grid to track pixel overwrites
                grid = [[-1 for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]
                overwrite_count = 0
                
                # Process each command
                for cmd_index, command in enumerate(commands):
                    cells, color = self.parse_command(command)
                    
                    for row, col in cells:
                        # Check if this cell has already been written to
                        if 0 <= row-1 < self.grid_size[0] and 0 <= col < self.grid_size[1]:
                            if grid[row-1][col] != -1:
                                overwrite_count += 1
                            grid[row-1][col] = cmd_index
                
                # Store results for this flag
                results['flags'][country] = {
                    'command_count': len(commands),
                    'is_efficient': len(commands) <= 3,
                    'overwrite_count': overwrite_count
                }
            
            return results
            
        except Exception as e:
            print(f"Error analyzing {json_info['path']}: {str(e)}")
            return None
    
    def run_analysis(self):
        """Run the analysis on all JSON files."""
        self.find_json_files()
        
        for json_info in self.json_files:
            results = self.analyze_json_file(json_info)
            if results:
                key = (results['ai_folder'], results['subfolder'])
                self.results[key] = results
        
        self.generate_report()
    
    def generate_report(self):
        """Generate a comprehensive report of the analysis results."""
        if not self.results:
            print("No results to report.")
            return
        
        # Prepare data for the report
        report_data = []
        
        for (ai_folder, subfolder), results in self.results.items():
            # Calculate total commands and overwrites
            total_commands = sum(flag_data['command_count'] for flag_data in results['flags'].values())
            total_overwrites = sum(flag_data['overwrite_count'] for flag_data in results['flags'].values())
            
            # Check if Sweden and Germany are done efficiently
            sweden_efficient = results['flags'].get('Sweden', {}).get('is_efficient', False)
            germany_efficient = results['flags'].get('Germany', {}).get('is_efficient', False)
            
            # Add to report data
            report_data.append({
                'AI Model': ai_folder,
                'Subfolder': subfolder,
                'Total Commands': total_commands,
                'Total Overwrites': total_overwrites,
                'Sweden Efficient': sweden_efficient,
                'Germany Efficient': germany_efficient,
                'Avg Commands Per Flag': total_commands / len(results['flags']) if results['flags'] else 0
            })
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(report_data)
        
        # Save to CSV
        df.to_csv('flag_efficiency_report.csv', index=False)
        
        # Generate detailed JSON report
        detailed_report = {
            'summary': {
                'total_ai_models': len(set(item['AI Model'] for item in report_data)),
                'total_subfolders': len(report_data),
                'most_efficient_model': df.loc[df['Total Commands'].idxmin()]['AI Model'] if not df.empty else None,
                'least_overwrites_model': df.loc[df['Total Overwrites'].idxmin()]['AI Model'] if not df.empty else None
            },
            'ai_models': {}
        }
        
        # Organize by AI model
        for (ai_folder, subfolder), results in self.results.items():
            if ai_folder not in detailed_report['ai_models']:
                detailed_report['ai_models'][ai_folder] = {'subfolders': {}}
            
            detailed_report['ai_models'][ai_folder]['subfolders'][subfolder] = {
                'total_commands': sum(flag_data['command_count'] for flag_data in results['flags'].values()),
                'total_overwrites': sum(flag_data['overwrite_count'] for flag_data in results['flags'].values()),
                'flags': {
                    country: {
                        'commands': flag_data['command_count'],
                        'is_efficient': flag_data['is_efficient'],
                        'overwrites': flag_data['overwrite_count']
                    }
                    for country, flag_data in results['flags'].items()
                }
            }
        
        # Save detailed report
        with open('flag_efficiency_detailed.json', 'w') as f:
            json.dump(detailed_report, f, indent=4)
        
        # Generate visualizations
        self.generate_visualizations(df)
        
        print("Analysis complete. Reports saved to:")
        print("- flag_efficiency_report.csv")
        print("- flag_efficiency_detailed.json")
        print("- Visualization images in the current directory")
    
    def generate_visualizations(self, df):
        """Generate visualizations of the analysis results."""
        # Set up the figure size
        plt.figure(figsize=(15, 10))
        
        # 1. Total Commands by AI Model and Subfolder
        plt.subplot(2, 2, 1)
        df_pivot = df.pivot_table(index='AI Model', columns='Subfolder', values='Total Commands', aggfunc='sum')
        df_pivot.plot(kind='bar', ax=plt.gca())
        plt.title('Total Commands by AI Model and Subfolder')
        plt.ylabel('Number of Commands')
        plt.xticks(rotation=45)
        plt.legend(title='Subfolder')
        
        # 2. Total Overwrites by AI Model and Subfolder
        plt.subplot(2, 2, 2)
        df_pivot = df.pivot_table(index='AI Model', columns='Subfolder', values='Total Overwrites', aggfunc='sum')
        df_pivot.plot(kind='bar', ax=plt.gca())
        plt.title('Total Overwrites by AI Model and Subfolder')
        plt.ylabel('Number of Overwrites')
        plt.xticks(rotation=45)
        plt.legend(title='Subfolder')
        
        # 3. Average Commands Per Flag
        plt.subplot(2, 2, 3)
        df_pivot = df.pivot_table(index='AI Model', columns='Subfolder', values='Avg Commands Per Flag', aggfunc='mean')
        df_pivot.plot(kind='bar', ax=plt.gca())
        plt.title('Average Commands Per Flag')
        plt.ylabel('Avg Commands')
        plt.xticks(rotation=45)
        plt.legend(title='Subfolder')
        
        # 4. Efficiency for Sweden and Germany
        plt.subplot(2, 2, 4)
        
        # Count efficient implementations by AI model
        efficiency_data = defaultdict(lambda: {'Sweden': 0, 'Germany': 0, 'Total': 0})
        for _, row in df.iterrows():
            ai_model = row['AI Model']
            efficiency_data[ai_model]['Sweden'] += 1 if row['Sweden Efficient'] else 0
            efficiency_data[ai_model]['Germany'] += 1 if row['Germany Efficient'] else 0
            efficiency_data[ai_model]['Total'] += 1
        
        # Prepare data for plotting
        ai_models = list(efficiency_data.keys())
        sweden_efficient = [efficiency_data[ai]['Sweden'] for ai in ai_models]
        germany_efficient = [efficiency_data[ai]['Germany'] for ai in ai_models]
        
        # Create grouped bar chart
        x = np.arange(len(ai_models))
        width = 0.35
        
        plt.bar(x - width/2, sweden_efficient, width, label='Sweden')
        plt.bar(x + width/2, germany_efficient, width, label='Germany')
        
        plt.title('Number of Efficient Implementations (≤3 commands)')
        plt.ylabel('Count')
        plt.xlabel('AI Model')
        plt.xticks(x, ai_models, rotation=45)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('flag_efficiency_charts.png')
        
        # Create a separate chart for efficiency percentage
        plt.figure(figsize=(12, 6))
        
        # Calculate percentages
        sweden_pct = [efficiency_data[ai]['Sweden'] / efficiency_data[ai]['Total'] * 100 for ai in ai_models]
        germany_pct = [efficiency_data[ai]['Germany'] / efficiency_data[ai]['Total'] * 100 for ai in ai_models]
        
        plt.bar(x - width/2, sweden_pct, width, label='Sweden')
        plt.bar(x + width/2, germany_pct, width, label='Germany')
        
        plt.title('Percentage of Efficient Implementations (≤3 commands)')
        plt.ylabel('Percentage')
        plt.xlabel('AI Model')
        plt.xticks(x, ai_models, rotation=45)
        plt.legend()
        plt.ylim(0, 100)
        
        # Add percentage labels
        for i, v in enumerate(sweden_pct):
            plt.text(i - width/2, v + 2, f'{v:.1f}%', ha='center')
        
        for i, v in enumerate(germany_pct):
            plt.text(i + width/2, v + 2, f'{v:.1f}%', ha='center')
        
        plt.tight_layout()
        plt.savefig('flag_efficiency_percentage.png')

if __name__ == "__main__":
    analyzer = FlagEfficiencyAnalyzer()
    analyzer.run_analysis()
    print("Analysis complete!")
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import random
import os
from PIL import Image, ImageTk
import io

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver")
        self.root.geometry("1000x600")
        
        # Maze properties
        self.maze_size = 15  # Default size
        self.cell_size = 30
        self.player_pos = [1, 1]  # Start position
        self.current_seed = random.randint(1, 1000000)  # Random seed for maze generation
        self.maze = self.generate_maze(self.maze_size, self.maze_size, self.current_seed)
        self.goal_pos = [self.maze_size - 2, self.maze_size - 2]  # Goal position
        
        # Path tracking
        self.path_visited = set([(1, 1)])  # Track visited cells
        self.move_count = 0  # Track number of moves
        
        # Command history
        self.command_history = []
        self.current_attempt_name = "Player"
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for maze display
        left_frame = tk.Frame(main_frame, width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for maze
        self.canvas_frame = tk.Frame(left_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Seed input frame
        seed_frame = tk.Frame(left_frame)
        seed_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(seed_frame, text="Seed:").pack(side=tk.LEFT)
        self.seed_entry = tk.Entry(seed_frame, width=10)
        self.seed_entry.pack(side=tk.LEFT, padx=5)
        self.seed_entry.insert(0, str(self.current_seed))
        
        tk.Button(seed_frame, text="Apply Seed", command=self.apply_seed).pack(side=tk.LEFT, padx=5)
        tk.Button(seed_frame, text="Random Seed", command=self.random_seed).pack(side=tk.LEFT, padx=5)
        
        # Maze size slider
        size_frame = tk.Frame(left_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(size_frame, text="Maze Size:").pack(side=tk.LEFT)
        self.size_slider = tk.Scale(size_frame, from_=5, to=25, orient=tk.HORIZONTAL, 
                                   length=200, command=self.update_maze_size)
        self.size_slider.set(self.maze_size)
        self.size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons under maze
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="New Maze", command=self.new_maze).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Copy Maze", command=self.copy_maze).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset Position", command=self.reset_position).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Path", command=self.clear_path).pack(side=tk.LEFT, padx=5)
        
        # Right frame for commands
        right_frame = tk.Frame(main_frame, width=500)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Command input
        command_label = tk.Label(right_frame, text="Enter Commands:")
        command_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.command_text = scrolledtext.ScrolledText(right_frame, height=10)
        self.command_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Name input for attempts
        name_frame = tk.Frame(right_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(name_frame, text="Attempt Name:").pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.name_entry.insert(0, "Player")
        
        # Buttons for commands
        button_frame2 = tk.Frame(right_frame)
        button_frame2.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame2, text="Execute Commands", command=self.execute_commands).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame2, text="Load from JSON", command=self.load_from_json).pack(side=tk.LEFT, padx=5)
        
        # Command history display
        history_label = tk.Label(right_frame, text="Command History:")
        history_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.history_text = scrolledtext.ScrolledText(right_frame, height=10)
        self.history_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # Draw initial maze
        self.draw_maze()
    
    def generate_maze(self, width, height, seed=None):
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
        
        # Initialize maze with walls
        maze = [['#' for _ in range(width)] for _ in range(height)]
        
        # Use depth-first search to generate a proper maze
        # Start with all cells as walls
        # Then carve passages using DFS with backtracking
        
        # Only work with odd-indexed cells to ensure walls between all passages
        stack = [(1, 1)]
        visited = set([(1, 1)])
        
        # Mark the start as a passage
        maze[1][1] = ' '
        
        # Directions: right, down, left, up
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        
        while stack:
            current_row, current_col = stack[-1]
            
            # Find unvisited neighbors
            neighbors = []
            for dr, dc in directions:
                new_row, new_col = current_row + dr, current_col + dc
                if (0 < new_row < height - 1 and 0 < new_col < width - 1 and 
                    (new_row, new_col) not in visited):
                    neighbors.append((new_row, new_col, dr, dc))
            
            if neighbors:
                # Choose a random unvisited neighbor
                new_row, new_col, dr, dc = random.choice(neighbors)
                
                # Remove the wall between current cell and chosen cell
                maze[current_row + dr//2][current_col + dc//2] = ' '
                
                # Mark the chosen cell as a passage
                maze[new_row][new_col] = ' '
                
                # Add the chosen cell to visited set and stack
                visited.add((new_row, new_col))
                stack.append((new_row, new_col))
            else:
                # Backtrack
                stack.pop()
        
        # Ensure the goal is open
        maze[height-2][width-2] = ' '
        
        # Reset random seed to avoid affecting other random operations
        random.seed()
        
        return maze
    
    def draw_maze(self):
        self.canvas.delete("all")
        
        # Calculate canvas size
        canvas_width = self.maze_size * self.cell_size
        canvas_height = self.maze_size * self.cell_size
        
        # Configure canvas
        self.canvas.config(width=canvas_width, height=canvas_height)
        
        # Draw maze
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                if self.maze[i][j] == '#':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="")
                else:
                    # Check if this cell is in the path
                    if (i, j) in self.path_visited:
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="light blue", outline="gray")
                    else:
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")
        
        # Draw goal
        goal_x, goal_y = self.goal_pos[1] * self.cell_size, self.goal_pos[0] * self.cell_size
        self.canvas.create_rectangle(
            goal_x, goal_y, 
            goal_x + self.cell_size, goal_y + self.cell_size, 
            fill="green", outline=""
        )
        
        # Draw player
        player_x, player_y = self.player_pos[1] * self.cell_size, self.player_pos[0] * self.cell_size
        self.canvas.create_oval(
            player_x + 5, player_y + 5, 
            player_x + self.cell_size - 5, player_y + self.cell_size - 5, 
            fill="red", outline=""
        )
    
    def new_maze(self):
        self.random_seed()
    
    def reset_position(self):
        self.player_pos = [1, 1]
        self.path_visited = set([(1, 1)])
        self.move_count = 0
        self.draw_maze()
        self.update_history("Position reset to start")
    
    def copy_maze(self):
        """Create a text representation of the maze using emojis and copy it to clipboard"""
        # Create a text representation of the maze
        maze_text = ""
        
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                # Check if this is the player position
                if [i, j] == self.player_pos:
                    maze_text += "🟥"  # Red square for player
                # Check if this is the goal position
                elif [i, j] == self.goal_pos:
                    maze_text += "🟩"  # Green square for goal
                # Check if this is a wall
                elif self.maze[i][j] == '#':
                    maze_text += "⬛"  # Black square for walls
                # Otherwise it's a path
                else:
                    maze_text += "⬜"  # White square for paths
            
            # Add a newline at the end of each row
            maze_text += "\n"
        
        # Add seed information
        maze_text += f"\nMaze Seed: {self.current_seed}\n"
        maze_text += f"Maze Size: {self.maze_size}x{self.maze_size}\n"
        
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(maze_text)
        
        messagebox.showinfo("Success", "Maze copied to clipboard as emoji text")
    
    def execute_commands(self):
        # Get commands from text area
        command_text = self.command_text.get("1.0", tk.END).strip()
        if not command_text:
            messagebox.showinfo("Info", "No commands to execute")
            return
        
        # Get attempt name
        self.current_attempt_name = self.name_entry.get() or "Player"
        
        # Process commands
        commands = command_text.split('\n')
        
        # Add to history
        self.command_history.append({
            "name": self.current_attempt_name,
            "commands": commands
        })
        
        # Execute each command
        for cmd in commands:
            self.process_command(cmd)
    
    def process_command(self, command):
        command = command.strip().lower()
        if not command:
            return
        
        # Parse command
        parts = command.split()
        
        if len(parts) < 2 or parts[0] != "move":
            self.update_history(f"Invalid command: {command}")
            return
        
        direction = parts[1]
        steps = 1  # Default is 1 step
        
        # Check if steps are specified
        if len(parts) > 2:
            try:
                steps = int(parts[2])
            except ValueError:
                self.update_history(f"Invalid step count in: {command}")
                return
        
        # Process movement
        moves_made = 0
        for _ in range(steps):
            new_pos = self.player_pos.copy()
            
            if direction == "up":
                new_pos[0] -= 1
            elif direction == "down":
                new_pos[0] += 1
            elif direction == "left":
                new_pos[1] -= 1
            elif direction == "right":
                new_pos[1] += 1
            else:
                self.update_history(f"Unknown direction: {direction}")
                return
            
            # Check if the move is valid
            if (0 <= new_pos[0] < self.maze_size and 
                0 <= new_pos[1] < self.maze_size and 
                self.maze[new_pos[0]][new_pos[1]] != '#'):
                self.player_pos = new_pos
                # Add to path
                self.path_visited.add((new_pos[0], new_pos[1]))
                moves_made += 1
                self.move_count += 1
            else:
                self.update_history(f"Cannot move {direction} - wall or boundary")
                break
        
        if moves_made > 0:
            self.update_history(f"Moved {direction} {moves_made} step(s). Total moves: {self.move_count}")
        
        # Check if player reached the goal
        if self.player_pos == self.goal_pos:
            self.update_history(f"Goal reached in {self.move_count} moves! Congratulations!")
            messagebox.showinfo("Success", f"You've solved the maze in {self.move_count} moves!")
        
        # Update the maze display
        self.draw_maze()
    
    def update_history(self, message):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"{self.current_attempt_name}: {message}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def load_from_json(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Check if this is the new format with maze info
            if isinstance(data, dict) and "maze_info" in data and "attempts" in data:
                # Load maze info
                maze_info = data["maze_info"]
                if "seed" in maze_info and "size" in maze_info:
                    # Update maze size slider
                    self.size_slider.set(maze_info["size"])
                    
                    # Update seed entry
                    self.seed_entry.delete(0, tk.END)
                    self.seed_entry.insert(0, str(maze_info["seed"]))
                    
                    # Apply the seed and size
                    self.current_seed = maze_info["seed"]
                    self.maze_size = maze_info["size"]
                    self.maze = self.generate_maze(self.maze_size, self.maze_size, self.current_seed)
                    self.goal_pos = [self.maze_size - 2, self.maze_size - 2]
                    
                    # Get the attempts
                    attempts = data["attempts"]
                else:
                    messagebox.showwarning("Warning", "Maze information incomplete. Using current maze.")
                    attempts = data["attempts"]
            else:
                # Old format - just a list of attempts
                messagebox.showwarning("Warning", "Old format JSON without maze information. Using current maze.")
                attempts = data
            
            if not isinstance(attempts, list):
                messagebox.showerror("Error", "Invalid JSON format. Expected a list of attempts.")
                return
            
            # Reset position
            self.reset_position()
            
            # Clear command history display
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete("1.0", tk.END)
            self.history_text.config(state=tk.DISABLED)
            
            # Prepare performance report
            performance_report = []
            
            # Process each attempt
            for attempt in attempts:
                if "name" not in attempt or "commands" not in attempt:
                    continue
                
                self.current_attempt_name = attempt["name"]
                self.update_history(f"Starting attempt")
                
                # Reset path for each attempt
                self.path_visited = set([(1, 1)])
                self.player_pos = [1, 1]
                self.move_count = 0
                
                for cmd in attempt["commands"]:
                    self.process_command(cmd)
                
                # Record performance
                reached_goal = self.player_pos == self.goal_pos
                performance_report.append({
                    "name": self.current_attempt_name,
                    "moves": self.move_count,
                    "reached_goal": reached_goal,
                    "cells_visited": len(self.path_visited),
                    "maze_seed": self.current_seed,
                    "maze_size": self.maze_size
                })
                
                self.update_history(f"Attempt completed. Total moves: {self.move_count}")
            
            # Generate performance report file
            report_filename = os.path.splitext(filename)[0] + "_performance.json"
            with open(report_filename, 'w') as f:
                json.dump(performance_report, f, indent=2)
            
            # Display performance summary
            self.show_performance_summary(performance_report)
            
            messagebox.showinfo("Success", f"Loaded {len(attempts)} attempts from {filename}\nPerformance report saved to {report_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON: {str(e)}")
    
    def show_performance_summary(self, performance_report):
        """Display a summary of the performance report in a new window"""
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Performance Summary")
        summary_window.geometry("500x400")
        
        # Create a frame for the summary
        frame = tk.Frame(summary_window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label
        tk.Label(frame, text="Performance Summary", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Create a text widget to display the summary
        summary_text = scrolledtext.ScrolledText(frame, height=20, width=60)
        summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Sort performance by number of moves (if reached goal) or by cells visited
        def sort_key(item):
            if item["reached_goal"]:
                return (0, item["moves"])  # Reached goal, sort by moves
            else:
                return (1, -item["cells_visited"])  # Didn't reach goal, sort by cells visited (descending)
        
        sorted_report = sorted(performance_report, key=sort_key)
        
        # Add header
        summary_text.insert(tk.END, f"{'Rank':<5}{'Name':<15}{'Moves':<10}{'Goal':<10}{'Cells Visited':<15}\n")
        summary_text.insert(tk.END, "-" * 55 + "\n")
        
        # Add each attempt
        for i, attempt in enumerate(sorted_report, 1):
            goal_status = "Yes" if attempt["reached_goal"] else "No"
            summary_text.insert(tk.END, f"{i:<5}{attempt['name']:<15}{attempt['moves']:<10}{goal_status:<10}{attempt['cells_visited']:<15}\n")
        
        # Add statistics
        summary_text.insert(tk.END, "\nStatistics:\n")
        summary_text.insert(tk.END, "-" * 55 + "\n")
        
        # Calculate statistics
        completed_attempts = [a for a in performance_report if a["reached_goal"]]
        if completed_attempts:
            avg_moves = sum(a["moves"] for a in completed_attempts) / len(completed_attempts)
            min_moves = min(a["moves"] for a in completed_attempts)
            best_performer = next(a["name"] for a in performance_report if a["reached_goal"] and a["moves"] == min_moves)
            
            summary_text.insert(tk.END, f"Attempts that reached goal: {len(completed_attempts)}/{len(performance_report)}\n")
            summary_text.insert(tk.END, f"Average moves for successful attempts: {avg_moves:.1f}\n")
            summary_text.insert(tk.END, f"Best performance: {best_performer} ({min_moves} moves)\n")
        else:
            summary_text.insert(tk.END, "No attempts reached the goal.\n")
        
        # Make the text widget read-only
        summary_text.config(state=tk.DISABLED)
    
    def update_maze_size(self, val):
        new_size = int(val)
        if new_size != self.maze_size:
            self.maze_size = new_size
            self.maze = self.generate_maze(self.maze_size, self.maze_size, self.current_seed)
            self.goal_pos = [self.maze_size - 2, self.maze_size - 2]
            self.reset_position()
            self.draw_maze()

    def clear_path(self):
        # Keep only the current position in the path
        self.path_visited = set([(self.player_pos[0], self.player_pos[1])])
        self.draw_maze()
        self.update_history("Path cleared")

    def apply_seed(self):
        try:
            new_seed = int(self.seed_entry.get())
            self.current_seed = new_seed
            self.maze = self.generate_maze(self.maze_size, self.maze_size, self.current_seed)
            self.reset_position()
            self.draw_maze()
            self.update_history(f"Applied seed: {self.current_seed}")
        except ValueError:
            messagebox.showerror("Error", "Seed must be an integer")

    def random_seed(self):
        self.current_seed = random.randint(1, 1000000)
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, str(self.current_seed))
        self.maze = self.generate_maze(self.maze_size, self.maze_size, self.current_seed)
        self.reset_position()
        self.draw_maze()
        self.update_history(f"Generated random seed: {self.current_seed}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()

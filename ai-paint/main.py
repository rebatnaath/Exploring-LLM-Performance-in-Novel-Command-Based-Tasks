import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import re
from PIL import Image, ImageDraw
import json
import os

class AIPaint:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Paint")
        
        # Constants
        self.CANVAS_ROWS = 30  # Set row size to 30
        self.CANVAS_COLS = 50  # Set column size to 50
        self.PIXEL_SIZE = 12
        self.TOTAL_WIDTH = self.CANVAS_COLS * self.PIXEL_SIZE  # Width for 50 columns
        self.TOTAL_HEIGHT = self.CANVAS_ROWS * self.PIXEL_SIZE  # Height for 30 rows
        
        # Store current JSON data
        self.current_json = None
        
        # Grid coordinates (A-Z followed by a-z for columns)
        uppercase = [chr(i) for i in range(65, 91)]  # A to Z
        lowercase = [chr(i) for i in range(97, 97 + 24)]  # a to x
        self.col_labels = uppercase + lowercase  # First 26 uppercase, then a-x
        self.row_labels = list(range(1, self.CANVAS_ROWS + 1))  # 1 to 30
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create canvas frame
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create column headers (A, B, C, etc.)
        self.col_header_canvas = tk.Canvas(
            self.canvas_frame,
            width=self.TOTAL_WIDTH + self.PIXEL_SIZE,
            height=self.PIXEL_SIZE,
            bg='white'
        )
        self.col_header_canvas.grid(row=0, column=1, sticky=tk.W)
        
        # Draw column labels
        for i, label in enumerate(self.col_labels):
            x = i * self.PIXEL_SIZE + self.PIXEL_SIZE/2
            self.col_header_canvas.create_text(x, self.PIXEL_SIZE/2, text=label, anchor="center")
        
        # Create row labels canvas
        self.row_label_canvas = tk.Canvas(
            self.canvas_frame,
            width=self.PIXEL_SIZE,
            height=self.TOTAL_HEIGHT,
            bg='white'
        )
        self.row_label_canvas.grid(row=1, column=0, sticky=tk.N)
        
        # Draw row labels
        for i, label in enumerate(self.row_labels):
            y = i * self.PIXEL_SIZE + self.PIXEL_SIZE/2
            self.row_label_canvas.create_text(self.PIXEL_SIZE/2, y, text=str(label), anchor="center")
        
        # Create main canvas
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.TOTAL_WIDTH,
            height=self.TOTAL_HEIGHT,
            bg='white'
        )
        self.canvas.grid(row=1, column=1)
        
        # Store canvas rectangles for better performance
        self.rectangles = {}
        
        # Create right side panel for commands
        self.command_frame = ttk.Frame(self.main_frame, padding="5")
        self.command_frame.grid(row=0, column=1, rowspan=2, padx=10, sticky=(tk.N, tk.S))
        
        # Add label for commands
        ttk.Label(self.command_frame, text="Commands:").grid(row=0, column=0, sticky=tk.W)
        
        # Create command text area
        self.command_text = scrolledtext.ScrolledText(
            self.command_frame,
            width=30,
            height=20,
            wrap=tk.WORD
        )
        self.command_text.grid(row=1, column=0, pady=5)
        
        # Example commands
        example_commands = """# Example commands:
# You can use color names:
bg:black
a1-d5:green
f4-g3:purple

# Color individual cells with commas:
l5,n5:red
a1,b1,c1:blue

# Or hex color codes:
a1-c3:#ff0000
d4-f6:#00ff00

# Common colors:
# - red, green, blue, yellow
# - black, white, gray/grey
# - purple, orange, pink
# - Or any hex color: #RRGGBB

# Enter your commands here
# One command per line"""
        self.command_text.insert('1.0', example_commands)
        
        # Create buttons frame
        self.button_frame = ttk.Frame(self.command_frame)
        self.button_frame.grid(row=2, column=0, pady=5)
        
        # Create execute button
        self.execute_button = ttk.Button(
            self.button_frame,
            text="Execute All",
            command=self.process_all_commands
        )
        self.execute_button.grid(row=0, column=0, padx=5)
        
        # Create clear button
        self.clear_button = ttk.Button(
            self.button_frame,
            text="Clear Canvas",
            command=self.clear_canvas
        )
        self.clear_button.grid(row=0, column=1)
        
        # Create save button
        self.save_button = ttk.Button(
            self.button_frame,
            text='Save Image',
            command=self.save_canvas
        )
        self.save_button.grid(row=0, column=2)
        
        # Create load JSON button
        self.load_json_button = ttk.Button(
            self.button_frame,
            text="Load JSON",
            command=self.load_json
        )
        self.load_json_button.grid(row=0, column=3, padx=5)
        
        # Initialize the grid
        self.draw_grid()

    def draw_grid(self):
        """Draw the initial grid"""
        self.canvas.delete("all")  # Clear existing rectangles
        self.rectangles.clear()
        
        for row in range(self.CANVAS_ROWS):
            for col in range(self.CANVAS_COLS):
                x1 = col * self.PIXEL_SIZE
                y1 = row * self.PIXEL_SIZE
                x2 = x1 + self.PIXEL_SIZE
                y2 = y1 + self.PIXEL_SIZE
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill='white',
                    outline='gray'
                )
                self.rectangles[(col, row)] = rect_id

    def convert_coord_to_pixel(self, coord):
        """Convert grid coordinate (e.g., 'A1') to pixel position"""
        if not coord or len(coord) < 2:
            return None
            
        # Split coordinate into column and row
        col_part = ''.join(c for c in coord if c.isalpha())  # Keep case as is
        row_part = ''.join(c for c in coord if c.isdigit())
        
        if not col_part or not row_part:
            return None
            
        # Convert column letters to number (A=0, B=1, etc.)
        col = 0
        for char in col_part:
            if char.isupper():
                col = col * 26 + (ord(char) - ord('A'))
            else:
                col = col * 26 + (ord(char) - ord('a') + 26)  # Adjust for lowercase letters
            
        try:
            row = int(row_part) - 1
            if 0 <= col < self.CANVAS_COLS and 0 <= row < self.CANVAS_ROWS:
                return (col, row)
        except ValueError:
            return None
        
        return None

    def fill_pixel(self, col, row, color):
        """Fill a single pixel with the specified color"""
        if (col, row) in self.rectangles:
            self.canvas.itemconfig(self.rectangles[(col, row)], fill=color)

    def fill_range(self, start_coord, end_coord, color):
        """Fill a range of pixels with the specified color"""
        start = self.convert_coord_to_pixel(start_coord)
        end = self.convert_coord_to_pixel(end_coord)
        
        if not start or not end:
            return False
            
        start_col, start_row = start
        end_col, end_row = end
        
        # Ensure start is before end
        start_col, end_col = min(start_col, end_col), max(start_col, end_col)
        start_row, end_row = min(start_row, end_row), max(start_row, end_row)
        
        # Use canvas.update_idletasks() periodically for better responsiveness
        update_counter = 0
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                self.fill_pixel(col, row, color)
                update_counter += 1
                if update_counter % 100 == 0:  # Update every 100 pixels
                    self.canvas.update_idletasks()
        
        return True

    def process_command(self, command):
        """Process a single painting command"""
        command = command.strip()  # Remove only leading/trailing whitespace
        if not command or command.startswith('#'):
            return True
            
        try:
            # Process background command
            if command.startswith('bg:'):
                color = command[3:].strip()
                # Fill the entire canvas
                for row in range(self.CANVAS_ROWS):
                    for col in range(self.CANVAS_COLS):
                        self.fill_pixel(col, row, color)
                    if row % 5 == 0:  # Update every 5 rows for responsiveness
                        self.canvas.update_idletasks()
                return True
            
            # Process range command (e.g., a1-d5:green) or comma-separated cells (e.g., l5,n5:red)
            range_match = re.match(r'([a-zA-Z0-9,\-]+):(.+)', command)
            if range_match:
                cells, color = range_match.groups()
                if '-' in cells:  # Range format (a1-d5)
                    start, end = cells.split('-')
                    return self.fill_range(start, end, color)
                else:  # Comma-separated format (l5,n5)
                    all_valid = True
                    for cell in cells.split(','):
                        coord = self.convert_coord_to_pixel(cell.strip())
                        if coord:
                            col, row = coord
                            self.fill_pixel(col, row, color)
                        else:
                            all_valid = False
                    return all_valid
            
        except Exception as e:
            print(f"Error processing command '{command}': {str(e)}")  # Log the error
            return False  # Indicate that the command was not processed successfully

        return False

    def process_all_commands(self):
        """Process all commands in the text area"""
        commands = self.command_text.get('1.0', tk.END).split('\n')
        for command in commands:
            if command.strip() and not command.strip().startswith('#'):
                if not self.process_command(command):
                    messagebox.showerror("Error", f"Invalid command: {command}")
                    return

    def clear_canvas(self):
        """Clear the canvas back to white"""
        for row in range(self.CANVAS_ROWS):
            for col in range(self.CANVAS_COLS):
                self.fill_pixel(col, row, 'white')
            if row % 5 == 0:  # Update every 5 rows for responsiveness
                self.canvas.update_idletasks()

    def save_canvas(self):
        # Open a file dialog to choose the save location and filename
        file_path = filedialog.asksaveasfilename(defaultextension='.png',
                                                   filetypes=[('PNG files', '*.png'), ('JPEG files', '*.jpg;*.jpeg'), ('All files', '*.*')])
        if not file_path:
            return  # User canceled the dialog

        # Create a new image with white background
        image = Image.new('RGB', (self.TOTAL_WIDTH, self.TOTAL_HEIGHT), 'white')
        draw = ImageDraw.Draw(image)

        # Draw each rectangle on the image without an outline
        for (col, row), rect_id in self.rectangles.items():
            x1 = col * self.PIXEL_SIZE
            y1 = row * self.PIXEL_SIZE
            x2 = x1 + self.PIXEL_SIZE
            y2 = y1 + self.PIXEL_SIZE
            color = self.canvas.itemcget(rect_id, 'fill')
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=color)  # Set outline to the same color

        # Save the image
        image.save(file_path)  # Save to the chosen file path
        messagebox.showinfo('Image Saved', f'The canvas has been saved as {file_path}')

    def load_json(self):
        """Load commands from a JSON file"""
        file_path = filedialog.askopenfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')]
        )
        if not file_path:
            return

        try:
            # Check if the file is empty
            if os.path.getsize(file_path) == 0:
                raise ValueError("The selected JSON file is empty.")

            with open(file_path, 'r') as f:
                self.current_json = json.load(f)
            
            # Check if this is a flags collection
            if 'flags' in self.current_json:
                # Process each flag
                for flag in self.current_json['flags']:
                    # Clear the canvas for each new flag
                    self.clear_canvas()
                    
                    # Set the commands in the text area
                    if 'commands' in flag:
                        self.command_text.delete('1.0', tk.END)
                        self.command_text.insert('1.0', '\n'.join(flag['commands']))
                        
                        # Execute the commands and handle errors
                        for command in flag['commands']:
                            if not self.process_command(command):
                                print(f"Invalid command for {flag['title']}: {command}")  # Log the error
                                continue  # Skip to the next command
                        
                        # Save the result with the flag's title
                        if 'title' in flag:
                            self.save_canvas_with_title(flag['title'])
                            
                messagebox.showinfo('Success', 'All flags have been processed and saved!')
            else:
                # Handle single command set (old format)
                self.clear_canvas()
                if 'commands' in self.current_json:
                    self.command_text.delete('1.0', tk.END)
                    self.command_text.insert('1.0', '\n'.join(self.current_json['commands']))
                    self.process_all_commands()
                    if 'title' in self.current_json:
                        self.save_canvas_with_title(self.current_json['title'])
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON: {str(e)}")

    def save_canvas_with_title(self, title):
        """Save the canvas with the specified title"""
        # Create filename from title
        filename = f"{title}.png"
        
        # Create directory if it doesn't exist
        os.makedirs('flags', exist_ok=True)
        
        # Create a new image with white background
        image = Image.new('RGB', (self.TOTAL_WIDTH, self.TOTAL_HEIGHT), 'white')
        draw = ImageDraw.Draw(image)

        # Draw each rectangle on the image without an outline
        for (col, row), rect_id in self.rectangles.items():
            x1 = col * self.PIXEL_SIZE
            y1 = row * self.PIXEL_SIZE
            x2 = x1 + self.PIXEL_SIZE
            y2 = y1 + self.PIXEL_SIZE
            color = self.canvas.itemcget(rect_id, 'fill')
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=color)

        # Save the image in the flags directory
        filepath = os.path.join('flags', filename)
        image.save(filepath)
        print(f'Saved flag: {filepath}')

def main():
    root = tk.Tk()
    app = AIPaint(root)
    root.mainloop()

if __name__ == "__main__":
    main()
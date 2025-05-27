import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import pandas as pd
from datetime import datetime
from PIL import Image, ImageTk
import shutil

class MealPlannerInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Meal Planner")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Soft Mint Palette
        BG_MAIN = "#f8fffa"
        BG_FRAME = "#e3fcec"
        BG_BUTTON = "#b2f7ef"
        FG_TEXT = "#222831"

        # Set main window background
        self.root.configure(bg=BG_MAIN)

        # Use clam theme for a modern look
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TButton", padding=8, font=("Helvetica", 11), background=BG_BUTTON, foreground=FG_TEXT)
        style.map("TButton", background=[("active", BG_FRAME)])
        style.configure("TLabel", padding=6, font=("Helvetica", 11), background=BG_FRAME, foreground=FG_TEXT)
        style.configure("TLabelframe", background=BG_FRAME, foreground=FG_TEXT)
        style.configure("TLabelframe.Label", font=("Helvetica", 13, "bold"), background=BG_FRAME, foreground=FG_TEXT)
        style.configure("TEntry", font=("Helvetica", 11), fieldbackground=BG_FRAME, foreground=FG_TEXT)
        style.configure("Main.TFrame", background=BG_MAIN)

        # Center the window
        self.center_window(800, 600)

        # Main frame
        self.main_frame = ttk.Frame(root, padding=25, style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(self.main_frame, text="Meal Planner", font=('Helvetica', 22, 'bold'), background=BG_MAIN, foreground=FG_TEXT)
        title_label.pack(pady=(0, 18))

        # File selection section
        self.create_file_section(BG_FRAME, FG_TEXT)
        
        # Process buttons section
        self.create_process_section(BG_FRAME, FG_TEXT, BG_BUTTON)
        
        # Output display section
        self.create_output_section(BG_FRAME, FG_TEXT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", background=BG_FRAME, foreground=FG_TEXT)
        status_bar.pack(fill=tk.X, pady=(8, 0))
        
        # Initialize file paths
        self.meal_plan_path = None
        self.ingredients_path = None
        
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_file_section(self, bg_frame, fg_text):
        # Meal plan file selection
        file_frame = ttk.LabelFrame(self.main_frame, text="Select Files", padding=18, style="TLabelframe")
        file_frame.pack(fill=tk.X, pady=12)
        file_frame.configure(style="TLabelframe")
        ttk.Label(file_frame, text="Meal Plan File:", background=bg_frame, foreground=fg_text).grid(row=0, column=0, sticky="w", padx=7, pady=7)
        self.meal_plan_entry = ttk.Entry(file_frame, width=45)
        self.meal_plan_entry.grid(row=0, column=1, padx=7, pady=7)
        ttk.Button(file_frame, text="Browse", command=self.browse_meal_plan).grid(row=0, column=2, padx=7, pady=7)
        
        # Ingredients file selection
        ttk.Label(file_frame, text="Ingredients File:", background=bg_frame, foreground=fg_text).grid(row=1, column=0, sticky="w", padx=7, pady=7)
        self.ingredients_entry = ttk.Entry(file_frame, width=45)
        self.ingredients_entry.grid(row=1, column=1, padx=7, pady=7)
        ttk.Button(file_frame, text="Browse", command=self.browse_ingredients).grid(row=1, column=2, padx=7, pady=7)
    
    def create_process_section(self, bg_frame, fg_text, bg_button):
        process_frame = ttk.LabelFrame(self.main_frame, text="Processes", padding=18, style="TLabelframe")
        process_frame.pack(fill=tk.X, pady=12)
        process_frame.configure(style="TLabelframe")
        # Add button to run main_model_old.py as the first step
        self.run_main_model_old_btn = ttk.Button(
            process_frame, text="Run Ingredient Cost Calculation",
            command=self.run_main_model_old
        )
        self.run_main_model_old_btn.grid(row=0, column=0, padx=12, pady=7, sticky="ew")
        # Shift other buttons to the right
        self.calc_costs_btn = ttk.Button(process_frame, text="Calculate Costs", command=self.calculate_costs)
        self.calc_costs_btn.grid(row=0, column=1, padx=12, pady=7, sticky="ew")
        self.gen_plan_btn = ttk.Button(process_frame, text="Generate Daily Plan", command=self.generate_daily_plan)
        self.gen_plan_btn.grid(row=0, column=2, padx=12, pady=7, sticky="ew")
        self.view_results_btn = ttk.Button(process_frame, text="View Results", command=self.view_results)
        self.view_results_btn.grid(row=0, column=3, padx=12, pady=7, sticky="ew")
        self.view_plots_btn = ttk.Button(process_frame, text="View Visualizations", command=self.view_visualizations)
        self.view_plots_btn.grid(row=0, column=4, padx=12, pady=7, sticky="ew")
    
    def create_output_section(self, bg_frame, fg_text):
        # Output text area
        output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding=18, style="TLabelframe")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=12)
        output_frame.configure(style="TLabelframe")
        
        self.output_text = tk.Text(output_frame, height=12, font=("Consolas", 11), bg="#f8fffa", fg=fg_text)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for output
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text['yscrollcommand'] = scrollbar.set
    
    def browse_meal_plan(self):
        filename = filedialog.askopenfilename(
            title="Select Meal Plan File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.meal_plan_path = filename
            self.meal_plan_entry.delete(0, tk.END)
            self.meal_plan_entry.insert(0, filename)
    
    def browse_ingredients(self):
        filename = filedialog.askopenfilename(
            title="Select Ingredients File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.ingredients_path = filename
            self.ingredients_entry.delete(0, tk.END)
            self.ingredients_entry.insert(0, filename)
    
    def calculate_costs(self):
        if not self.meal_plan_path or not self.ingredients_path:
            messagebox.showerror("Error", "Please select both meal plan and ingredients files")
            return
        
        try:
            self.status_var.set("Calculating costs...")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Calculating costs...\n")
            self.root.update()
            
            # Run the cost calculation script
            result = subprocess.run(['python', 'calculate_daily_costs.py'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                self.output_text.insert(tk.END, result.stdout)
                self.status_var.set("Cost calculation completed")
                messagebox.showinfo("Success", "Cost calculation completed successfully!")
            else:
                self.output_text.insert(tk.END, f"Error: {result.stderr}")
                self.status_var.set("Error in cost calculation")
                messagebox.showerror("Error", "Failed to calculate costs")
        
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self.status_var.set("Error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def generate_daily_plan(self):
        if not self.meal_plan_path:
            messagebox.showerror("Error", "Please select a meal plan file")
            return
        
        try:
            self.status_var.set("Generating daily plan...")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Generating daily plan...\n")
            self.root.update()
            
            # Run the daily plan generation script
            result = subprocess.run(['python', 'generate_daily_plan.py'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                self.output_text.insert(tk.END, result.stdout)
                self.status_var.set("Daily plan generation completed")
                messagebox.showinfo("Success", "Daily plan generated successfully!")
            else:
                self.output_text.insert(tk.END, f"Error: {result.stderr}")
                self.status_var.set("Error in plan generation")
                messagebox.showerror("Error", "Failed to generate daily plan")
        
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self.status_var.set("Error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def view_visualizations(self):
        plots_dir = os.path.join("output", "plots")
        if not os.path.exists(plots_dir):
            messagebox.showerror("Error", "No visualization plots found. Please run cost calculation first.")
            return

        plots_window = tk.Toplevel(self.root)
        plots_window.title("Cost Distribution Visualizations")
        plots_window.geometry("900x700")

        canvas = tk.Canvas(plots_window, bg="#f8fffa")
        scrollbar = ttk.Scrollbar(plots_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TLabelframe")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        for plot_file in sorted(os.listdir(plots_dir)):
            if plot_file.endswith('.png'):
                plot_frame = ttk.LabelFrame(scrollable_frame, text=plot_file.replace('.png', '').replace('_', ' ').title(), padding=10)
                plot_frame.grid(row=row, column=0, padx=20, pady=10, sticky="ew")

                try:
                    image_path = os.path.join(plots_dir, plot_file)
                    image = Image.open(image_path)
                    max_width = 700
                    if image.width > max_width:
                        ratio = max_width / image.width
                        image = image.resize((max_width, int(image.height * ratio)), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    label = ttk.Label(plot_frame, image=photo)
                    label.image = photo
                    label.pack(padx=5, pady=5)

                    # Save As button
                    def save_as(img_path=image_path):
                        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
                        if file_path:
                            shutil.copy(img_path, file_path)
                    ttk.Button(plot_frame, text="Save As PNG", command=save_as).pack(pady=5)

                except Exception as e:
                    ttk.Label(plot_frame, text=f"Error loading plot: {str(e)}").pack()

                row += 1

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        ttk.Button(plots_window, text="Close", command=plots_window.destroy).pack(pady=5)

    def view_results(self):
        output_dir = "output"
        if not os.path.exists(output_dir):
            messagebox.showerror("Error", "No output files found")
            return

        # Create a new window for results
        results_window = tk.Toplevel(self.root)
        results_window.title("Results")
        results_window.geometry("400x300")

        # Listbox to display file names
        file_listbox = tk.Listbox(results_window, width=50)
        file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add files to the listbox
        files = [f for f in os.listdir(output_dir) if f.endswith((".xlsx", ".csv"))]
        for file in files:
            file_listbox.insert(tk.END, file)

        # Add open button
        def open_file():
            selected = file_listbox.curselection()
            if selected:
                file = file_listbox.get(selected[0])
                os.startfile(os.path.join(output_dir, file))

        ttk.Button(results_window, text="Open Selected File", command=open_file).pack(pady=5)

    def run_main_model_old(self):
        try:
            self.status_var.set("Running ingredient cost calculation...")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Running ingredient cost calculation...\n")
            self.root.update()

            meal_plan_path = self.meal_plan_entry.get()
            ingredients_path = self.ingredients_entry.get()
            if not meal_plan_path or not ingredients_path:
                self.output_text.insert(tk.END, "Please select both meal plan and ingredients files.\n")
                self.status_var.set("Error: Missing file paths")
                messagebox.showerror("Error", "Please select both meal plan and ingredients files.")
                return

            result = subprocess.run([
                'python', 'main_model_old.py',
                meal_plan_path,
                ingredients_path
            ], capture_output=True, text=True)

            if result.returncode == 0:
                self.output_text.insert(tk.END, result.stdout)
                self.status_var.set("Ingredient cost calculation completed")
                messagebox.showinfo("Success", "Ingredient cost calculation completed successfully!")
            else:
                self.output_text.insert(tk.END, f"Error: {result.stderr}")
                self.status_var.set("Error in ingredient cost calculation")
                messagebox.showerror("Error", "Failed to run ingredient cost calculation")

        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self.status_var.set("Error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    app = MealPlannerInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
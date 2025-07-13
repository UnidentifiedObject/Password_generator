import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
import os # To check for file existence
from datetime import datetime # For adding timestamps to saved passwords

class PasswordGeneratorApp:
    def __init__(self, master):
        """
        Initializes the Tkinter GUI application for the password generator.
        """
        self.master = master
        master.title("Password Generator")
        master.geometry("550x550") # Adjusted size for new elements
        master.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # --- Input Variables ---
        self.password_length = tk.StringVar(value="12")
        self.num_passwords = tk.StringVar(value="1") # Number of passwords to generate
        self.include_lowercase = tk.BooleanVar(value=True)
        self.include_uppercase = tk.BooleanVar(value=True)
        self.include_digits = tk.BooleanVar(value=True)
        self.include_special = tk.BooleanVar(value=True)
        self.use_custom_special_chars = tk.BooleanVar(value=False)
        self.custom_special_chars = tk.StringVar(value="")

        self.current_generated_passwords = [] # To store passwords for saving

        # --- GUI Layout ---

        # Status/Error Message Label
        self.status_label = ttk.Label(master, text="", foreground="red")
        self.status_label.pack(pady=5)

        # Frame for input controls
        input_frame = ttk.LabelFrame(master, text="Password Criteria", padding="15 15 15 15")
        input_frame.pack(padx=20, pady=10, fill="x", expand=False)

        # Grid configuration for input_frame
        input_frame.columnconfigure(1, weight=1) # Allow second column to expand

        # Row 0: Password Length
        ttk.Label(input_frame, text="Password Length:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.length_entry = ttk.Entry(input_frame, textvariable=self.password_length, width=10)
        self.length_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.length_entry.bind("<KeyRelease>", self._validate_length_input)

        # Row 1: Number of Passwords
        ttk.Label(input_frame, text="Number of Passwords:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.num_passwords_entry = ttk.Entry(input_frame, textvariable=self.num_passwords, width=10)
        self.num_passwords_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        self.num_passwords_entry.bind("<KeyRelease>", self._validate_num_passwords_input)

        # Row 2: Character Type Checkbuttons
        ttk.Label(input_frame, text="Include Characters:").grid(row=2, column=0, sticky="nw", pady=5, padx=5)
        checkbox_frame = ttk.Frame(input_frame)
        checkbox_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Checkbutton(checkbox_frame, text="Lowercase (a-z)", variable=self.include_lowercase).pack(anchor="w")
        ttk.Checkbutton(checkbox_frame, text="Uppercase (A-Z)", variable=self.include_uppercase).pack(anchor="w")
        ttk.Checkbutton(checkbox_frame, text="Digits (0-9)", variable=self.include_digits).pack(anchor="w")
        ttk.Checkbutton(checkbox_frame, text="Special (!@#$%)", variable=self.include_special).pack(anchor="w")

        # Row 3: Custom Special Characters
        self.custom_special_checkbox = ttk.Checkbutton(input_frame, text="Use Custom Special Chars:", variable=self.use_custom_special_chars,
                                                       command=self._toggle_custom_special_entry)
        self.custom_special_checkbox.grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.custom_special_entry = ttk.Entry(input_frame, textvariable=self.custom_special_chars, width=30, state='disabled')
        self.custom_special_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

        # Generate Button
        self.generate_button = ttk.Button(master, text="Generate Password(s)", command=self.generate_password_gui)
        self.generate_button.pack(pady=10)

        # Save Passwords Button (NEW)
        self.save_passwords_button = ttk.Button(master, text="Save Passwords to File", command=self._save_passwords_to_file)
        self.save_passwords_button.pack(pady=5)
        self.save_passwords_button.config(state='disabled') # Disable until passwords are generated

        # Output Display (using Text widget for multiple passwords)
        self.output_label_header = ttk.Label(master, text="Your Generated Password(s):")
        self.output_label_header.pack(pady=(5, 2))

        self.generated_password_display = tk.Text(master, height=8, width=50, state='disabled', wrap='word', font=('TkDefaultFont', 10))
        self.generated_password_display.pack(pady=(0, 10), padx=20, fill="both", expand=True)

        # Initialize custom special chars entry state
        self._toggle_custom_special_entry()

    def _validate_length_input(self, event=None):
        """Validates that the length entry only contains digits and is positive."""
        current_text = self.password_length.get()
        if not current_text.isdigit() and current_text != "":
            self.password_length.set("".join(filter(str.isdigit, current_text)))
            self.status_label.config(text="Length must be a number.")
        elif current_text == "":
            self.status_label.config(text="Length cannot be empty.")
        elif int(current_text) <= 0:
            self.status_label.config(text="Length must be positive.")
        else:
            self.status_label.config(text="") # Clear error message

    def _validate_num_passwords_input(self, event=None):
        """Validates that the number of passwords entry only contains digits and is positive, with a limit."""
        current_text = self.num_passwords.get()
        if not current_text.isdigit() and current_text != "":
            self.num_passwords.set("".join(filter(str.isdigit, current_text)))
            self.status_label.config(text="Number of passwords must be a number.")
        elif current_text == "":
            self.status_label.config(text="Number of passwords cannot be empty.")
        elif int(current_text) <= 0:
            self.status_label.config(text="Number of passwords must be positive.")
        elif int(current_text) > 10: # Set a limit for multiple passwords
            self.num_passwords.set("10")
            self.status_label.config(text="Max 10 passwords at a time for display.")
        else:
            self.status_label.config(text="") # Clear error message

    def _toggle_custom_special_entry(self):
        """Enables/disables the custom special characters entry based on checkbox state."""
        if self.use_custom_special_chars.get():
            self.custom_special_entry.config(state='normal')
        else:
            self.custom_special_entry.config(state='disabled')

    def _set_password_display(self, text_to_display):
        """Helper to set the text of the read-only password display Text widget."""
        self.generated_password_display.config(state='normal') # Temporarily enable to modify
        self.generated_password_display.delete(1.0, tk.END) # Delete all existing text
        self.generated_password_display.insert(tk.END, text_to_display)
        self.generated_password_display.config(state='disabled') # Set back to read-only

    def generate_password_gui(self):
        """
        Generates passwords based on GUI inputs and displays them.
        Handles input validation and error messages.
        """
        self.status_label.config(text="") # Clear previous status messages
        self._set_password_display("") # Clear previous passwords
        self.save_passwords_button.config(state='disabled') # Disable save button until new passwords are ready

        try:
            length = int(self.password_length.get())
            if length <= 0:
                self.status_label.config(text="Password length must be a positive number.")
                return
        except ValueError:
            self.status_label.config(text="Invalid password length. Please enter a number.")
            return

        try:
            num_passwords_to_generate = int(self.num_passwords.get())
            if num_passwords_to_generate <= 0:
                self.status_label.config(text="Number of passwords must be a positive number.")
                return
            if num_passwords_to_generate > 10: # Enforce the limit
                self.status_label.config(text="Maximum 10 passwords can be generated at once.")
                return
        except ValueError:
            self.status_label.config(text="Invalid number of passwords. Please enter a number.")
            return

        # Define character sets
        char_sets = {
            'lowercase': string.ascii_lowercase,
            'uppercase': string.ascii_uppercase,
            'digits': string.digits,
            'special': string.punctuation # Default special characters
        }

        # Use custom special characters if selected and provided
        if self.use_custom_special_chars.get():
            custom_specials = self.custom_special_chars.get()
            if not custom_specials:
                self.status_label.config(text="Custom special characters field cannot be empty if selected.")
                return
            char_sets['special'] = custom_specials

        # Build the pool of characters based on selected types
        all_possible_chars = []
        selected_types_for_guarantee = [] # To ensure at least one of each selected type is present

        if self.include_lowercase.get():
            all_possible_chars.extend(list(char_sets['lowercase']))
            selected_types_for_guarantee.append(char_sets['lowercase'])
        if self.include_uppercase.get():
            all_possible_chars.extend(list(char_sets['uppercase']))
            selected_types_for_guarantee.append(char_sets['uppercase'])
        if self.include_digits.get():
            all_possible_chars.extend(list(char_sets['digits']))
            selected_types_for_guarantee.append(char_sets['digits'])
        if self.include_special.get():
            all_possible_chars.extend(list(char_sets['special']))
            selected_types_for_guarantee.append(char_sets['special'])

        # Validate that at least one character type is selected
        if not all_possible_chars:
            self.status_label.config(text="Please select at least one character type.")
            return

        self.current_generated_passwords = [] # Reset for new generation
        for i in range(num_passwords_to_generate):
            current_guaranteed_chars = []
            # Ensure at least one of each selected type is present
            for char_set in selected_types_for_guarantee:
                current_guaranteed_chars.append(secrets.choice(char_set))

            # Adjust length if it's too short for guaranteed characters
            effective_length = max(length, len(current_guaranteed_chars))
            if effective_length > length:
                 # Only show warning once per generation click, not per password
                if i == 0:
                    messagebox.showwarning(
                        "Length Adjustment",
                        f"Password length ({length}) is too short for selected types ({len(current_guaranteed_chars)}).\n"
                        f"Generating with length {effective_length} for this password."
                    )

            remaining_length = effective_length - len(current_guaranteed_chars)

            # Generate remaining characters using secrets for quantum-inspired randomness
            random_fill_chars = [secrets.choice(all_possible_chars) for _ in range(remaining_length)]

            # Combine and shuffle for maximum unpredictability
            password_list = current_guaranteed_chars + random_fill_chars
            secrets.SystemRandom().shuffle(password_list) # Cryptographically strong shuffle

            self.current_generated_passwords.append("".join(password_list))

        self._set_password_display("\n".join(self.current_generated_passwords))
        self.status_label.config(text=f"{num_passwords_to_generate} password(s) generated successfully!", foreground="green")
        self.save_passwords_button.config(state='normal') # Enable save button after generation

    def _save_passwords_to_file(self):
        """Saves the currently generated passwords to a text file with a timestamp."""
        if not self.current_generated_passwords:
            self.status_label.config(text="No passwords to save. Generate some first!", foreground="red")
            return

        file_name = "passwords.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open(file_name, 'a') as f: # 'a' mode appends to the file
                f.write(f"--- Passwords generated on {timestamp} ---\n")
                for password in self.current_generated_passwords:
                    f.write(f"{password}\n")
                f.write("\n") # Add an extra newline for separation
            self.status_label.config(text=f"Passwords saved to {file_name}!", foreground="blue")
        except Exception as e:
            self.status_label.config(text=f"Error saving passwords: {e}", foreground="red")


# Main part of the script to run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()

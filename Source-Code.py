import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageFilter
from customtkinter import (
    CTk,
    CTkButton,
    CTkLabel,
    set_appearance_mode,
    CTkFrame,
    CTkSlider,
    CTkToplevel,
)


class PhotoEditor:
    def __init__(self):
        self.original_img = None
        self.modified_img = None
        self.original_image_tk = None
        self.modified_image_tk = None
        self.file_path_var = None
        self.history = []
        self.image_history = []

    def setup_gui(self):
        # Main Window
        self.root = CTk()
        self.root.title("Ứng dụng chỉnh sửa ảnh")
        self.root.geometry("1450x810")
        self.root.state("zoomed")  # Start in fullscreen mode
        set_appearance_mode("dark")

        # Layout Configuration
        self.root.rowconfigure(0, weight=7)  # Top row: Images
        self.root.rowconfigure(1, weight=3)  # Bottom row: Buttons
        self.root.columnconfigure(0, weight=5)  # Original Image
        self.root.columnconfigure(1, weight=5)  # Modified Image
        self.root.columnconfigure(2, weight=2)  # History Panel

        # Original Image Frame
        self.original_image_label = CTkLabel(self.root, text="Ảnh gốc")
        self.original_image_label.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10
        )

        # Modified Image Frame
        self.modified_image_label = CTkLabel(self.root, text="Ảnh đã chỉnh sửa")
        self.modified_image_label.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10
        )

        # History Panel
        self.history_panel = CTkLabel(
            self.root,
            text="Lịch sử:\nChưa có chỉnh sửa",
            justify="left",
            anchor="nw",
        )
        self.history_panel.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Button Frame
        button_frame = CTkFrame(self.root)
        button_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        button_frame.columnconfigure(tuple(range(8)), weight=1)

        # Create Buttons
        self.create_buttons(button_frame)

        # Footer Label
        footer_label = CTkLabel(
            self.root,
            text="Nhóm 2 - Xử lý thị giác",
            font=("Arial", 20),
            fg_color="green",
        )
        footer_label.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=10)

    def create_buttons(self, frame):
        button_configs = [
            ("Upload Image", self.upload_image, "green"),
            ("Save", self.save_image, "green"),
            ("Undo", self.undo_last_action, "green"),
            ("Brightness", self.show_brightness_slider, "red"),
            ("Contrast", self.adjust_contrast, "red"),
            ("Grayscale", self.apply_grayscale, "red"),
            ("Invert", self.invert_colors, "red"),
            ("Flip Horizontal", self.flip_horizontal, "red"),
            ("Flip Vertical", self.flip_vertical, "red"),
            ("Rotate", self.rotate_image, "red"),
            ("Crop", self.start_cropping, "red"),
            ("Blur", self.apply_blur, "red"),
            ("Posterize", self.posterize_image, "red"),
        ]

        for idx, (text, command, color) in enumerate(button_configs):
            btn = CTkButton(
                frame, text=text, command=command, fg_color=color, font=("Arial", 16)
            )
            btn.grid(row=idx // 8, column=idx % 8, sticky="nsew", padx=10, pady=10)

    
    def show_brightness_slider(self):
        if not self.modified_img:
            messagebox.showerror("Error", "No image loaded!")
            return

        # Create a dialog window for brightness adjustment
        brightness_dialog = CTkToplevel(self.root)
        brightness_dialog.title("Adjust Brightness")
        brightness_dialog.geometry("400x200")

        # Create a label to show current value
        value_label = CTkLabel(brightness_dialog, text="Brightness: 1.0")
        value_label.pack(pady=10)

        # Create slider
        def update_brightness(value):
            value = float(value)
            value_label.configure(text=f"Brightness: {value:.2f}")
            
            # Apply brightness in real-time
            modified = self.apply_image_filter(ImageEnhance.Brightness, value)
            if modified:
                self.modified_img = modified
                self.display_images()

        slider = CTkSlider(
            brightness_dialog, 
            from_=0.0, 
            to=2.0, 
            number_of_steps=40, 
            command=update_brightness
        )
        slider.set(1.0)  # Default to no change
        slider.pack(padx=20, pady=20, fill='x')

        # Confirmation button
        def confirm_brightness():
            self.log_history(f"Brightness set to {slider.get():.2f}")
            brightness_dialog.destroy()

        confirm_btn = CTkButton(
            brightness_dialog, 
            text="Confirm", 
            command=confirm_brightness
        )
        confirm_btn.pack(pady=10)

    def show_contrast_slider(self):
        if not self.modified_img:
            messagebox.showerror("Error", "No image loaded!")
            return

        # Create a dialog window for contrast adjustment
        contrast_dialog = tk.Toplevel(self.root)
        contrast_dialog.title("Adjust Contrast")
        contrast_dialog.geometry("400x200")

        # Create a label to show current value
        value_label = CTkLabel(contrast_dialog, text="Contrast: 1.0")
        value_label.pack(pady=10)

        # Create slider
        def update_contrast(value):
            value_label.configure(text=f"Contrast: {value:.2f}")
            
            # Apply contrast in real-time
            modified = self.apply_image_filter(ImageEnhance.Contrast, value)
            if modified:
                self.modified_img = modified
                self.display_images()

        slider = CTkSlider(
            contrast_dialog, 
            from_=0.0, 
            to=2.0, 
            number_of_steps=40, 
            command=update_contrast
        )
        slider.set(1.0)  # Default to no change
        slider.pack(padx=20, pady=20, fill='x')

        # Confirmation button
        def confirm_contrast():
            self.log_history(f"Contrast set to {slider.get():.2f}")
            contrast_dialog.destroy()

        confirm_btn = CTkButton(
            contrast_dialog, 
            text="Confirm", 
            command=confirm_contrast
        )
        confirm_btn.pack(pady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if not file_path:
            return
        try:
            self.file_path_var = file_path
            self.original_img = Image.open(file_path)
            self.modified_img = self.original_img.copy()
            self.display_images()
            self.log_history("Uploaded Image")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def save_image(self):
        if not self.modified_img:
            messagebox.showerror("Error", "No image to save!")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")],
        )
        if not file_path:
            return
        try:
            self.modified_img.save(file_path)
            messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

    def display_images(self):
        if self.original_img:
            original_resized = self.resize_image(self.original_img)
            self.original_image_tk = ImageTk.PhotoImage(original_resized)
            self.original_image_label.configure(image=self.original_image_tk)

        if self.modified_img:
            modified_resized = self.resize_image(self.modified_img)
            self.modified_image_tk = ImageTk.PhotoImage(modified_resized)
            self.modified_image_label.configure(image=self.modified_image_tk)

    def resize_image(self, image):
        max_size = (400, 400)
        return image.copy().resize(max_size, Image.Resampling.LANCZOS)

    def log_history(self, action, save_image=True):
        if not self.modified_img:
            return

        self.history.append(action)
        
        if save_image:
            self.image_history.append(self.modified_img.copy())
        
        self.update_history()

    def apply_image_filter(self, filter_func, *args):
        if not self.modified_img:
            messagebox.showerror("Error", "No image loaded!")
            return None

        try:
            # Apply the filter
            if filter_func == ImageFilter.GaussianBlur:
                modified = self.modified_img.filter(filter_func(radius=args[0]))
            elif filter_func in [ImageEnhance.Brightness, ImageEnhance.Contrast]:
                enhancer = filter_func(self.modified_img)
                modified = enhancer.enhance(args[0])
            else:
                modified = filter_func(self.modified_img)

            # Ensure the modified image is a PIL Image object
            if not isinstance(modified, Image.Image):
                modified = Image.fromarray(modified)

            return modified
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {e}")
            return None
        
    def adjust_brightness(self):
        modified = self.apply_image_filter(ImageEnhance.Brightness, 1.2)
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Brightness Increased")

    def adjust_contrast(self):
        modified = self.apply_image_filter(ImageEnhance.Contrast, 1.5)
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Contrast Increased")

    def apply_grayscale(self):
        modified = self.apply_image_filter(ImageOps.grayscale)
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Grayscale Applied")

    def invert_colors(self):
        modified = self.apply_image_filter(ImageOps.invert)
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Colors Inverted")

    def flip_horizontal(self):
        modified = self.apply_image_filter(ImageOps.mirror)
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Flipped Horizontally")

    def flip_vertical(self):
        modified = self.apply_image_filter(ImageOps.flip)
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Flipped Vertically")

    def rotate_image(self):
        modified = self.apply_image_filter(lambda img: img.transpose(Image.ROTATE_90))
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Rotated 90°")

    def apply_blur(self):
        modified = self.apply_image_filter(ImageFilter.GaussianBlur, 2)
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Blur Applied")

    def posterize_image(self):
        modified = self.apply_image_filter(lambda img: ImageOps.posterize(img, 2))
        if modified:
            self.modified_img = modified
            self.display_images()
            self.log_history("Posterized")

    def start_cropping(self):
        messagebox.showinfo("Info", "Cropping is not yet implemented!")

    def undo_last_action(self):
        if len(self.history) > 1:
            self.history.pop()  # Remove last action
            self.image_history.pop()  # Remove last image
            if self.image_history:  # Check if list is not empty
                self.modified_img = self.image_history[-1]  # Restore previous image
            else:
                self.modified_img = self.original_img.copy()  # Restore original image
            self.display_images()
            self.update_history()
        else:
            messagebox.showinfo("Info", "No more actions to undo!")

    def update_history(self):
        self.history_panel.configure(text="Lịch sử:\n" + "\n".join(self.history))

    def run(self):
        self.setup_gui()
        self.root.mainloop()


if __name__ == "__main__":
    editor = PhotoEditor()
    editor.run()
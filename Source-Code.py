import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageFilter
from customtkinter import (
    CTk,
    CTkButton,
    CTkLabel,
    set_appearance_mode,
    CTkFrame,
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
            ("Undo", self.undo_last_action, "blue"),
            ("Brightness", self.adjust_brightness, "orange"),
            ("Contrast", self.adjust_contrast, "orange"),
            ("Grayscale", self.apply_grayscale, "red"),
            ("Invert", self.invert_colors, "red"),
            ("Flip Horizontal", self.flip_horizontal, "red"),
            ("Flip Vertical", self.flip_vertical, "red"),
            ("Rotate", self.rotate_image, "orange"),
            ("Crop", self.start_cropping, "orange"),
            ("Blur", self.apply_blur, "orange"),
            ("Posterize", self.posterize_image, "red"),
            ("Pencil", self.apply_pencil_effect, "red"),
        ]

        for idx, (text, command, color) in enumerate(button_configs):
            btn = CTkButton(
                frame, text=text, command=command, fg_color=color, font=("Arial", 12)
            )
            btn.grid(row=idx // 8, column=idx % 8, sticky="nsew", padx=5, pady=5)

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
            self.history = ["Uploaded Image"]
            self.update_history()
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

    def adjust_brightness(self):
        self.apply_filter(ImageEnhance.Brightness, 1.2, action_text="Brightness Increased")

    def adjust_contrast(self):
        self.apply_filter(ImageEnhance.Contrast, 1.5, action_text="Contrast Increased")

    def apply_grayscale(self):
        self.apply_filter(ImageOps.grayscale, None, action_text="Grayscale Applied")

    def invert_colors(self):
        self.apply_filter(ImageOps.invert, None, action_text="Colors Inverted")

    def flip_horizontal(self):
        self.apply_filter(ImageOps.mirror, None, action_text="Flipped Horizontally")

    def flip_vertical(self):
        self.apply_filter(ImageOps.flip, None, action_text="Flipped Vertically")

    def rotate_image(self):
        self.apply_filter(lambda img: img.rotate(90), None, action_text="Rotated 90°")

    def apply_blur(self):
        self.apply_filter(ImageFilter.GaussianBlur, radius=2, action_text="Blur Applied")

    def posterize_image(self):
        self.apply_filter(lambda img: ImageOps.posterize(img, 2), action_text="Posterized")

    def apply_pencil_effect(self):
        self.apply_filter(ImageFilter.CONTOUR, None, action_text="Pencil Effect Applied")

    def start_cropping(self):
        messagebox.showinfo("Info", action_text="Cropping is not yet implemented!")

    def apply_filter(self, filter_func, *args, action_text):
        if not self.modified_img:
            messagebox.showerror("Error", "No image loaded!")
            return
        try:
            # Apply the filter
            if args and args[0] is not None:
                if hasattr(filter_func(self.modified_img), 'enhance'):
                    self.modified_img = filter_func(self.modified_img).enhance(args[0])
                else:
                    self.modified_img = filter_func(self.modified_img, *args)
            else:
                self.modified_img = filter_func(self.modified_img)

            # Update the history
            self.history.append(action_text)
            self.image_history.append(self.modified_img.copy())
            self.display_images()
            self.update_history()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {e}")

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
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageOps,
    ImageTk,
)
from customtkinter import (
    CTk,
    CTkButton,
    CTkLabel,
    set_appearance_mode,
    CTkFrame,
    CTkSlider,
)

class PhotoEditor:
    def __init__(self):
        self.zoom_factor = 3
        self.threshold = 128
        self.recent_operations = []
        self.original_img = None
        self.modified_img = None

    def setup_gui(self):
        self.root = CTk()
        self.root.resizable(False, False)
        self.root.title("Ứng dụng chỉnh sửa ảnh")
        self.root.geometry("1300x660")
        set_appearance_mode("dark")
        
        # Setup image display areas
        self.original_image_label = CTkLabel(self.root, text="Ảnh gốc", width=280, height=280)
        self.original_image_label.place(x=250, y=5)
        
        self.modified_image_label = CTkLabel(self.root, text="Ảnh đã chỉnh sửa", width=280, height=280)
        self.modified_image_label.place(x=550, y=5)
        
        self.file_path_var = tk.StringVar()
        
        # Setup buttons
        self.create_buttons()
        
        # Setup history panel
        self.history_panel = CTkLabel(self.root, text="Lịch sử", width=180, height=200, justify="left", anchor="nw")
        self.history_panel.place(x=900, y=5)
        
        # Setup title
        name_label = CTkLabel(
            self.root, 
            text="Nhóm 2 - Xử lý thị giác", 
            font=("Arial", 20), 
            fg_color="green"
        )
        name_label.place(x=600, y=650, anchor="s")

    def create_buttons(self):
        # Upload button
        upload_button = CTkButton(
            self.root,
            text="Upload Image",
            command=self.upload_image,
            fg_color="green",
            font=("consolas", 12),
        )
        upload_button.place(x=450, y=280)

        # Create button frames
        button_frame_1 = CTkFrame(self.root)
        button_frame_1.place(x=2, y=330)
        
        button_frame_2 = CTkFrame(self.root)
        button_frame_2.place(x=2, y=390)
        
        button_frame_3 = CTkFrame(self.root)
        button_frame_3.place(x=200, y=440)

        # Define button configurations
        button_configs = [
            # Frame 1 buttons
            (button_frame_1, [
                ("Brightness", "Brightness"),
                ("Contrast", "Contrast"),
                ("Blur", "Blur"),
                ("Vintage", "Vintage"),
                ("Black", "Black"),
                ("Flip Horizontal", "Flip Horizontal"),
                ("Flip Vertical", "Flip Vertical"),
            ]),
            # Frame 2 buttons
            (button_frame_2, [
                ("Grayscale", "Grayscale"),
                ("Rotate", "Rotate"),
                ("Sepia", "Sepia"),
                ("Pencil", "Pencil"),
                ("Posterize", "Posterize"),
                ("Sharpen", "Sharpen"),
            ]),
            # Frame 3 buttons
            (button_frame_3, [
                ("Zoom In", "Zoom"),
                ("Invert", "Invert"),
                ("Solarize", "Solarize"),
                ("Save", "Save"),
                ("Undo", "Undo"),
            ])
        ]

        # Create buttons
        for frame, buttons in button_configs:
            for text, command in buttons:
                if command == "Save":
                    btn = CTkButton(frame, text=text, command=self.save_image, fg_color="green")
                elif command == "Undo":
                    btn = CTkButton(frame, text=text, command=lambda: self.perform_operation("Undo"), fg_color="blue")
                elif command == "Brightness":
                    btn = CTkButton(frame, text=text, command=self.open_brightness_slider, fg_color="orange")
                elif command == "Contrast":
                    btn = CTkButton(frame, text=text, command=self.open_contrast_slider, fg_color="orange")
                elif command == "Blur":
                    btn = CTkButton(frame, text=text, command=self.open_blur_slider, fg_color="orange")
                elif command == "Rotate":
                    btn = CTkButton(frame, text=text, command=self.open_rotation_slider, fg_color="orange")
                else:
                    btn = CTkButton(
                        frame,
                        text=text,
                        command=lambda cmd=command: self.perform_operation(cmd),
                        fg_color="red"
                    )
                btn.pack(side=tk.LEFT, padx=5)

    def open_brightness_slider(self):
        if self.check_image_loaded():
            self.create_slider("Adjust Brightness", self.adjust_brightness)

    def open_contrast_slider(self):
        if self.check_image_loaded():
            self.create_slider("Adjust Contrast", self.adjust_contrast)

    def open_blur_slider(self):
        if self.check_image_loaded():
            self.create_slider("Adjust Blur", self.adjust_blur, from_=0, to=10)

    def open_rotation_slider(self):
        if self.check_image_loaded():
            self.create_slider("Adjust Rotation", self.adjust_rotation, from_=0, to=360)

    def create_slider(self, title, command, from_=0, to=2):
        slider_window = Toplevel(self.root)
        slider_window.title(title)
        slider_window.geometry("300x100")
        slider = CTkSlider(slider_window, from_=from_, to=to, command=command)
        slider.pack(pady=20)
        slider.set(from_)  # Default value
        slider_window.protocol("WM_DELETE_WINDOW", lambda: self.on_slider_close(slider, title))

    def check_image_loaded(self):
        if not self.original_img:
            messagebox.showinfo("Thông báo", "Vui lòng tải lên hình ảnh trước")
            return False
        return True

    def on_slider_close(self, slider, title):
        value = slider.get()
        self.recent_operations.append(f"{title}: {value}")
        self.update_history_panel()
        slider.master.destroy()

    def update_image_label(self, label, img):
        try:
            img.thumbnail((280, 280))
            photo = ImageTk.PhotoImage(img)
            label.configure(image=photo)
            label.image = photo
            label.photo = img
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update image: {str(e)}")

    def save_image(self):
        if self.modified_img:
            output_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*"),
                ],
            )
            if output_path:
                try:
                    self.modified_img.save(output_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {str(e)}")

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.file_path_var.set(file_path)
                self.original_img = Image.open(file_path)
                self.modified_img = self.original_img.copy()
                self.update_image_label(self.original_image_label, self.original_img)
                self.update_image_label(self.modified_image_label, self.modified_img)
                self.original_image_label.configure(text="")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def perform_operation(self, operation):
        if operation == "Undo" and self.original_img:
            self.modified_img = self.original_img.copy()
            self.update_image_label(self.modified_image_label, self.modified_img)
            self.recent_operations.pop() if self.recent_operations else None
            self.update_history_panel()
            return

        input_image = self.file_path_var.get()
        if not input_image:
            messagebox.showinfo("Prompt", "Please upload an image first")
            return

        try:
            # Image processing operations
            operations = {
                "Grayscale": lambda img: img.convert("L"),
                "Sepia": lambda img: ImageOps.colorize(img.convert("L"), "#704214", "#C0A080"),
                "Flip Horizontal": lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),
                "Flip Vertical": lambda img: img.transpose(Image.FLIP_TOP_BOTTOM),
                "Zoom": lambda img: img.resize((int(img.size[0] * self.zoom_factor), 
                                              int(img.size[1] * self.zoom_factor)), 
                                              Image.BICUBIC),
                "Invert": lambda img: ImageOps.invert(img),
                "Solarize": lambda img: ImageOps.solarize(img, self.threshold),
                "Posterize": lambda img: ImageOps.posterize(img, 4),
                "Smart": self.smart_enhance,
                "Vintage": self.vintage_effect,
                "Black": lambda img: ImageEnhance.Contrast(img.convert("L")).enhance(2.0),
                "Pencil": self.pencil_sketch_effect
            }

            if operation in operations:
                self.modified_img = operations[operation](self.modified_img)
                self.update_image_label(self.modified_image_label, self.modified_img)
                self.recent_operations.append(operation)
                self.update_history_panel()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply {operation}: {str(e)}")

    def smart_enhance(self, img):
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = ImageEnhance.Brightness(img).enhance(1.1)
        img = img.filter(ImageFilter.SHARPEN)
        return ImageEnhance.Color(img).enhance(1.1)

    def vintage_effect(self, img):
        grayscale = img.convert("L")
        return Image.merge(
            "RGB",
            (
                grayscale.point(lambda p: p * 0.9 + 10),
                grayscale.point(lambda p: p * 0.95 + 20),
                grayscale.point(lambda p: p * 0.85)
            )
        )

    def pencil_sketch_effect(self, img):
        grayscale = img.convert("L")
        inverted = ImageOps.invert(grayscale)
        blur = inverted.filter(ImageFilter.GaussianBlur(radius=10))
        return Image.blend(grayscale, blur, alpha=0.45)

    def adjust_brightness(self, value):
        if self.original_img:
            enhancer = ImageEnhance.Brightness(self.original_img)
            self.modified_img = enhancer.enhance(float(value))
            self.update_image_label(self.modified_image_label, self.modified_img)

    def adjust_contrast(self, value):
        if self.original_img:
            enhancer = ImageEnhance.Contrast(self.original_img)
            self.modified_img = enhancer.enhance(float(value))
            self.update_image_label(self.modified_image_label, self.modified_img)

    def adjust_blur(self, value):
        if self.original_img:
            self.modified_img = self.original_img.filter(ImageFilter.GaussianBlur(radius=float(value)))
            self.update_image_label(self.modified_image_label, self.modified_img)

    def adjust_rotation(self, value):
        if self.original_img:
            self.modified_img = self.original_img.rotate(float(value))
            self.update_image_label(self.modified_image_label, self.modified_img)

    def update_history_panel(self):
        if not self.recent_operations:
            self.history_panel.configure(text="Lịch sử:\nChưa có chỉnh sửa")
            return
        history_text = "Lịch sử:\n" + "\n".join(f"{i+1}. {op}" for i, op in enumerate(self.recent_operations))
        self.history_panel.configure(text=history_text)

    def run(self):
        self.setup_gui()
        self.root.mainloop()

if __name__ == "__main__":
    editor = PhotoEditor()
    editor.run()

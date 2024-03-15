import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

class RTSPStreamPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("RTSP Stream Player")

        # Read RTSP streams from file
        with open("rtsp-traffic-ga.txt", "r") as file:
            self.rtsp_urls = [line.strip() for line in file if line.strip()]

        self.selected_stream = tk.StringVar()
        self.selected_stream.set(self.rtsp_urls[0])

        self.create_menu_panel()
        self.create_stream_panel()

        self.cap = None

    def create_menu_panel(self):
        menu_frame = ttk.Frame(self.master)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        menu_label = ttk.Label(menu_frame, text="RTSP Streams Menu")
        menu_label.pack()

        self.stream_dropdown = ttk.Combobox(menu_frame, textvariable=self.selected_stream, values=self.rtsp_urls)
        self.stream_dropdown.pack(fill=tk.BOTH, expand=True)

        self.stream_dropdown.bind("<<ComboboxSelected>>", self.on_stream_select)

        self.close_button = ttk.Button(menu_frame, text="Close Stream", command=self.close_stream)
        self.close_button.pack(fill=tk.BOTH, expand=True)

    def create_stream_panel(self):
        self.stream_frame = ttk.Frame(self.master)
        self.stream_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stream_label = ttk.Label(self.stream_frame, text="RTSP Stream")
        self.stream_label.pack()

        self.stream_border = ttk.Frame(self.stream_frame, borderwidth=2, relief="groove")
        self.stream_border.pack(fill=tk.BOTH, expand=True)

        self.stream_viewer = tk.Label(self.stream_border)
        self.stream_viewer.pack(fill=tk.BOTH, expand=True)

    def on_stream_select(self, event):
        if self.cap is not None:
            self.release_previous_stream()  # Release the previous stream
        self.load_stream()  # Load the new stream

    def close_stream(self):
        if self.cap is not None:
            self.cap.release()  # Release the current stream
            self.stream_label.config(text="RTSP Stream")  # Reset the stream label
            self.stream_viewer.config(image=None)  # Clear the live feed window
            self.cap = None  # Set the VideoCapture object to None

    def release_previous_stream(self):
        if self.cap is not None:
            self.cap.release()  # Release the previous stream
            self.stream_label.config(text="RTSP Stream")  # Reset the stream label
            self.stream_viewer.config(image=None)  # Clear the current live feed window
            self.cap = None  # Set the VideoCapture object to None

    def load_stream(self):
        self.cap = cv2.VideoCapture(self.selected_stream.get())

        if not self.cap.isOpened():
            self.stream_label.config(text="Error: Couldn't open the stream")
            return

        self.stream_label.config(text="RTSP Stream: " + self.selected_stream.get())
        self.update_stream()

    def update_stream(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = self.resize_image(img, self.stream_viewer.winfo_width(), self.stream_viewer.winfo_height())
            img = ImageTk.PhotoImage(img)
            self.stream_viewer.img = img
            self.stream_viewer.config(image=img)
        else:
            self.stream_label.config(text="Error: Couldn't read frame")
            self.close_stream()  # Close the stream if frame reading fails
            return

        # Schedule the next update after 10 ms if the stream is still open
        if self.cap is not None and self.cap.isOpened():
            self.master.after(10, self.update_stream)

    def resize_image(self, image, width, height):
        return image.resize((width, height), Image.ANTIALIAS)

def main():
    root = tk.Tk()
    app = RTSPStreamPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import google.generativeai as genai  # pyright: ignore[reportMissingImports]
import requests


class CountdownTimer:
    """A customizable GUI countdown timer."""

    def __init__(self, master):
        self.master = master
        self.master.title("Countdown Timer")
        self.master.geometry("600x400")
        self.bg_color = "#90ee90"
        self.font_size = 48
        self.font_family = "Helvetica"
        self.bg_image = None
        self.bg_label = None

        self.target_date = datetime(2028, 1, 10)
        self.date_layout = "ymd"

        self._setup_widgets()
        self.update_timer()

    def _setup_widgets(self):
        # Wallpaper/image background
        self.bg_label = tk.Label(self.master)
        self.bg_label.place(relwidth=1, relheight=1)

        # Top controls frame
        top_frame = tk.Frame(self.master, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            top_frame, text="Set Wallpaper", command=self.set_wallpaper
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            top_frame, text="Set BG Color", command=self.set_bg_color
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            top_frame,
            text="Font Size -",
            command=lambda: self.change_font_size(-8)
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            top_frame,
            text="Font Size +",
            command=lambda: self.change_font_size(8)
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            top_frame,
            text="Minimize",
            command=self.minimize_window
        ).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            top_frame,
            text="Maximize",
            command=self.maximize_window
        ).pack(side=tk.LEFT, padx=5)

        # Entry and set date
        entry_frame = tk.Frame(self.master, bg=self.bg_color)
        entry_frame.pack(pady=10)

        self.entry = tk.Entry(
            entry_frame, font=(self.font_family, 16), width=12
        )
        self.entry.pack(side=tk.LEFT)
        self.update_entry()

        tk.Button(entry_frame, text="Set Date", command=self.set_date).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            entry_frame, text="Toggle Date Layout", command=self.toggle_layout
        ).pack(side=tk.LEFT, padx=5)

        # Adjustment buttons
        button_frame = tk.Frame(self.master, bg=self.bg_color)
        button_frame.pack(pady=5)

        tk.Button(
            button_frame,
            text="+1 Day",
            command=self.increment_day
        ).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            button_frame,
            text="-1 Day",
            command=self.decrement_day
        ).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            button_frame, text="+1 Year", command=self.increment_year
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame, text="-1 Year", command=self.decrement_year
        ).pack(side=tk.LEFT, padx=5)

        # Countdown display
        self.label = tk.Label(
            self.master,
            font=(self.font_family, self.font_size),
            bg=self.bg_color
        )
        self.label.pack(pady=20)

        # Chatbot frame
        chat_frame = tk.Frame(self.master, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.chat_log = tk.Text(chat_frame, height=8, state=tk.DISABLED)
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.chat_entry = tk.Entry(chat_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
       
        tk.Button(
            chat_frame,
            text="Ask Ollama",
            command=self.ask_ollama
        ).pack(side=tk.LEFT, padx=5)

        # Weather frame
        weather_frame = tk.Frame(self.master, bg=self.bg_color)
        weather_frame.pack(fill=tk.X, padx=10, pady=5)

        self.weather_entry = tk.Entry(weather_frame)
        self.weather_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(
            weather_frame,
            text="Get Weather",
            command=self.get_weather
        ).pack(side=tk.LEFT, padx=5)
        self.weather_label = tk.Label(weather_frame, text="", bg=self.bg_color)
        self.weather_label.pack(side=tk.LEFT, padx=5)

    def set_wallpaper(self):
        """Set a background image."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if file_path:
            image = Image.open(file_path)
            image = image.resize(
                (self.master.winfo_width(), self.master.winfo_height()),
                Image.Resampling.LANCZOS,
            )
            self.bg_image = ImageTk.PhotoImage(image)
            self.bg_label.config(image=self.bg_image)
            self.bg_label.lower()  # Send to back

    def set_bg_color(self):
        """Set background color."""
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.bg_color = color
            self.master.configure(bg=self.bg_color)
            self.label.config(bg=self.bg_color)
            for frame in self.master.winfo_children():
                if isinstance(frame, tk.Frame):
                    frame.config(bg=self.bg_color)

    def change_font_size(self, delta):
        """Increase or decrease font size."""
        self.font_size = max(8, self.font_size + delta)
        self.label.config(font=(self.font_family, self.font_size))

    def minimize_window(self):
        """Minimize the window."""
        self.master.iconify()

    def maximize_window(self):
        """Maximize the window."""
        self.master.attributes('-zoomed', True)

    def update_entry(self):
        """Update the date entry field based on current layout."""
        self.entry.delete(0, tk.END)
        if self.date_layout == "ymd":
            self.entry.insert(0, self.target_date.strftime("%Y-%m-%d"))
        else:
            self.entry.insert(0, self.target_date.strftime("%d-%m-%Y"))

    def set_date(self):
        """Set the countdown target date from the entry field."""
        try:
            if self.date_layout == "ymd":
                new_date = datetime.strptime(self.entry.get(), "%Y-%m-%d")
            else:
                new_date = datetime.strptime(self.entry.get(), "%d-%m-%Y")
            self.target_date = new_date
        except ValueError:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "Invalid date!")

    def increment_day(self):
        """Increment the target date by one day."""
        self.target_date += timedelta(days=1)
        self.update_entry()

    def decrement_day(self):
        """Decrement the target date by one day."""
        self.target_date -= timedelta(days=1)
        self.update_entry()

    def increment_year(self):
        """Increment the target date by one year, handling leap years."""
        try:
            self.target_date = self.target_date.replace(
                year=self.target_date.year + 1
            )
        except ValueError:
            self.target_date = self.target_date.replace(
                year=self.target_date.year + 1, day=28
            )
        self.update_entry()

    def decrement_year(self):
        """Decrement the target date by one year, handling leap years."""
        try:
            self.target_date = self.target_date.replace(
                year=self.target_date.year - 1
            )
        except ValueError:
            self.target_date = self.target_date.replace(
                year=self.target_date.year - 1, day=28
            )
        self.update_entry()

    def toggle_layout(self):
        """Toggle the date layout between YYYY-MM-DD and DD-MM-YYYY."""
        self.date_layout = "dmy" if self.date_layout == "ymd" else "ymd"
        self.update_entry()

    def update_timer(self):
        """Update the countdown display every second."""
        now = datetime.now()
        remaining_time = self.target_date - now

        if remaining_time.total_seconds() < 0:
            time_format = "00 Years 00 Days 00:00:00"
        else:
            years = remaining_time.days // 365
            days = remaining_time.days % 365
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = (
                f"{years:02} Years "
                f"{days:02} Days "
                f"{hours:02}:{minutes:02}:{seconds:02}"
            )
        self.label.config(text=time_format)
        self.master.after(1000, self.update_timer)

    def ask_gemini(self):
        """Send user input to Gemini AI and display response."""
        prompt = self.chat_entry.get()
        if not prompt:
            return
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"You: {prompt}\n")
        self.chat_entry.delete(0, tk.END)
        try:
            genai.configure(
                api_key="AIzaSyCosntqPa2pf9-XFeLB72HcJnKtmitixZ4"
            )  # Replace with your key
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            response = model.generate_content(prompt)
            answer = response.candidates[0].content.parts[0].text.strip()
        except Exception as e:
            answer = f"Error: {e}"
        self.chat_log.insert(tk.END, f"Gemini: {answer}\n")
        self.chat_log.config(state=tk.DISABLED)

    def ask_ollama(self):
        """Send user input to a local Ollama model and display response."""
        prompt = self.chat_entry.get()
        if not prompt:
            return
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"You: {prompt}\n")
        self.chat_entry.delete(0, tk.END)
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt}
            )
            answer = response.json().get("response", "No response.")
        except Exception as e:
            answer = f"Error: {e}"
        self.chat_log.insert(tk.END, f"Ollama: {answer}\n")
        self.chat_log.config(state=tk.DISABLED)

    def get_weather(self):
        """Stub for weather functionality."""
        self.weather_label.config(text="Weather feature not implemented.")


if __name__ == "__main__":
    root = tk.Tk()
    timer = CountdownTimer(root)
    root.mainloop()

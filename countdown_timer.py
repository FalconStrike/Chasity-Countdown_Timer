import tkinter as tk
from datetime import datetime, timedelta

class CountdownTimer:
    def __init__(self, master):
        self.master = master
        self.master.title("Countdown Timer")

        self.target_date = datetime(2028, 1, 10,)  # Set your target date here

        self.label = tk.Label(master, font=("Helvetica", 48))
        self.label.pack()

        self.update_timer()

    def update_timer(self):
        now = datetime.now()
        remaining_time = self.target_date - now

        years = remaining_time.days // 365
        days = remaining_time.days % 365
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_format = f"{years} Years {days} Days {hours:02}:{minutes:02}:{seconds:02}"
        self.label.config(text=time_format)

        self.master.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    timer = CountdownTimer(root)
    root.mainloop()

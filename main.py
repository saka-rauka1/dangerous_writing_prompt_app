import tkinter as tk
from tkinter import ttk, font, messagebox


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dangerous Writing Prompt App")
        self.geometry("800x600")
        # Spawn window in the center of the screen
        self.eval("tk::PlaceWindow . center")

        # Create main content frame
        self.mainframe = Mainframe(self)
        self.mainframe.grid(column=0, row=0, sticky="nsew")

        # Enable mainframe auto-resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class Mainframe(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Initialize tracking variables
        self.session_length = tk.IntVar()
        self.session_elapsed = tk.IntVar()
        self.inactivity_count_limit = 5
        self.inactivity_count = 0

        self.has_session_started = False
        self.has_session_ended = False
        self._increment_session_time_id = None
        self._increment_inactivity_count_id = None

        # Predefined session length options
        self.session_length_options = [1, 2, 3, 5, 10, 15, 20, 30, 60]

        # Setup fonts
        self.text_widget_font = font.Font(family="Arial", size=14)

        # Create menu bar widgets
        self.session_length_label = ttk.Label(self, text="Session Length (mins):")
        self.session_length_box = ttk.Combobox(self, width=3, textvariable=self.session_length)
        self.session_length_box["values"] = self.session_length_options
        self.session_length_box.set(1)  # Default session length 1 min
        self.reset_btn = ttk.Button(self, text="Restart", command=self.reset)

        # Create progressbar
        self.progress_bar = ttk.Progressbar(self, mode="determinate", variable=self.session_elapsed)

        # Create text widget
        self.text_widget = tk.Text(self)
        self.text_widget.config(font=self.text_widget_font)
        self.text_widget["wrap"] = "word"

        # Grid widgets
        self.session_length_label.grid(column=0, row=0, sticky="e", padx=10, pady=5)
        self.session_length_box.grid(column=1, row=0, sticky="w")
        self.reset_btn.grid(column=2, row=0, sticky="e", padx=10)
        self.progress_bar.grid(column=0, row=1, columnspan=3, sticky="ew")
        self.text_widget.grid(column=0, row=2, columnspan=3, sticky="nsew")

        # Enable content auto-resizing
        self.columnconfigure(0, weight=0)
        self.rowconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)

        # Event bindings
        self.text_widget.bind("<KeyPress>", self.on_text_entry)

    def on_text_entry(self, *args, **kwargs):
        # Reset inactivity timer
        if self._increment_inactivity_count_id:
            self.after_cancel(self._increment_inactivity_count_id)
            self.inactivity_count = 0

        # Start session timer if not already started or ended
        if not self.has_session_started and not self.has_session_ended:
            self.has_session_started = True
            # Update progressbar
            session_length_seconds = self.session_length.get() * 60.0
            self.progress_bar["maximum"] = session_length_seconds
            # Start timer
            self.after(0, self._increment_session_time)

        # Start inactivity timer if a session has not already ended
        if not self.has_session_ended:
            self.after(0, self._increment_inactivity_count())

    def _increment_session_time(self):
        count = self.session_elapsed.get()
        count += 1
        self.session_elapsed.set(count)
        session_length_seconds = self.session_length.get() * 60.0

        # Stop timer when session length reached
        if count == session_length_seconds:
            self.has_session_started = False
            self.success()
        else:
            self._increment_session_time_id = self.after(1000, self._increment_session_time)

    def _increment_inactivity_count(self):
        self.inactivity_count += 1
        if self.inactivity_count == self.inactivity_count_limit:
            self.fail()
        else:
            self._increment_inactivity_count_id = self.after(1000, self._increment_inactivity_count)

    def reset(self):
        # Clear event queue
        self.after_cancel(self._increment_session_time_id)
        self.after_cancel(self._increment_inactivity_count_id)
        self.has_session_started = False
        self.has_session_ended = False

        # Reset tracking variables
        self.session_length.set(1)
        self.session_elapsed.set(0)
        self.inactivity_count_limit = 5
        self.inactivity_count = 0

        # Reset text widget
        self.text_widget["state"] = "normal"
        self.text_widget.delete("0.0", tk.END)

    def success(self):
        # Clear event queue
        self.after_cancel(self._increment_session_time_id)
        self.after_cancel(self._increment_inactivity_count_id)

        # Disable new input and block new events
        self.text_widget["state"] = "disabled"
        self.has_session_ended = True

        # Flash message
        messagebox.showinfo(
            title="Success",
            message=f"You managed to type without significant interruption for "
                    f"{self.session_length.get()} minutes"
        )

    def fail(self):
        # Delete users work
        self.text_widget.delete("0.0", tk.END)

        # Clear event queue
        self.after_cancel(self._increment_session_time_id)
        self.after_cancel(self._increment_inactivity_count_id)

        # Disable new input and block new events
        self.text_widget["state"] = "disabled"
        self.has_session_ended = True

        # Flash message
        time = divmod(self.session_elapsed.get(), 60)
        messagebox.showinfo(
            title="Fail",
            message=f"You only managed to type without significant interruption for "
                    f"{time[0]} minutes and {time[1]} seconds"
        )


# todo Indicate how many seconds are left until session fails
# todo What happens when both timers end simultaneously?
if __name__ == '__main__':
    app = App()
    app.mainloop()

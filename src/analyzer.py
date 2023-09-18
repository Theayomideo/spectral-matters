import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import guilib

# State dictionary to maintain the program state
state = {
    "data": (None, None),
    "points": [],
    "canvas": None,
    "window": None,
    "Messages": None,
    "peaks": [],
    "callback_id": None
}

# ===============================
# Interactive Functions
# ===============================

def custom_write_to_textbox(box, content, clear=False):
    """Writes a line of text into the selected textbox with interactive updates.  
    Parameters:
    - box (tk.Text): The textbox where the content should be written.
    - content (str): The content to write in the textbox.
    - clear (bool, optional): If True, clears the textbox before writing. Defaults to False.
    """
    guilib.write_to_textbox(box, content, clear)
    box.see(tk.END)
    box.update_idletasks()
    
def custom_show_info_message(title, message):
    """Display an information message using a messagebox.
    Parameters:
    - title (str): The title of the messagebox.
    - message (str): The content of the messagebox.
    """
    messagebox.showinfo(title, message)

def custom_show_error_message(title, message):
    """Display an error message using a messagebox.
    Parameters:
    - title (str): The title of the messagebox.
    - message (str): The content of the messagebox.
    """
    messagebox.showerror(title, message)

# ===============================
# Core Program Functions
# ===============================

def reset_state(*args):
    """Resets the state variables based on provided arguments. 
    If no argument(s) is provided, all state variables are reset.
    Parameters:
    - *args (str): The state keys to reset.
    """
    if not args or "data" in args:
        state["data"] = None
    if not args or "peaks" in args:
        state["peaks"] = []
    if not args or "canvas" in args:
        if state["canvas"]:
            state["canvas"].get_tk_widget().destroy()
            state["canvas"] = None
        
def read_data(folder_path):
    """Reads all .txt data files from the given folder, sums up the intensities,
    and reports any faulty files.
    Parameters:
    - folder_path (str): The path to the folder containing the .txt data files.
    Returns:
    - tuple: Contains two arrays; one for kinetic energy and another for summed intensities.
    """
    kinetic_energy = None
    total_intensities = None
    faulty_files = []
    successful_files = 0
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            try:
                file_data = np.loadtxt(file_path).T
                if kinetic_energy is None:
                    kinetic_energy = file_data[0]
                    total_intensities = np.zeros_like(kinetic_energy)
                total_intensities += file_data[1]
                successful_files += 1
            except (ValueError, OSError, IOError):
                faulty_files.append(file_name)
                custom_write_to_textbox(state["messages"], f"Error processing file: {file_name}.\n")
    
    if successful_files == 0:
        custom_write_to_textbox(state["messages"], "No valid data found in the selected folder.\n")
        return None, None, faulty_files, successful_files
    
    return kinetic_energy, total_intensities, faulty_files, successful_files

def load_data():
    """Loads spectral data from a user-selected folder and updates the program state.
    This function allows the user to select a folder containing the measurements. 
    It then reads the data from these files, updates the global state with the loaded data, 
    and displays the contents of the selected folder in the messages box. 
    In case of faulty files, they are listed separately in the message box.
    """
    folder_path = guilib.open_folder_dialog("Select Data Folder")
    if folder_path:
        folder_name = os.path.basename(folder_path)
        
        if os.path.isdir(folder_path):
            custom_show_info_message("Info", f"You have selected this folder: {folder_name}")   
            custom_write_to_textbox(
            state["messages"],
            f"\n{folder_name} contains the following files:\n"
            )
            for file_name in os.listdir(folder_path):
                custom_write_to_textbox(state["messages"], f"  - {file_name}\n")  
        else:
            custom_show_error_message("Error", "Selected folder does not exist. Check again.") 
            return
        x_data, y_data, faulty_files, successful_files = read_data(folder_path)

        if x_data is not None and y_data is not None and successful_files > 0:
            state["data"] = (x_data, y_data)
            state["peaks"] = []
            if state["canvas"]:
                state["canvas"].get_tk_widget().destroy()
                state["canvas"] = None
            custom_write_to_textbox(state["messages"], "All valid data loaded successfully!\n")
            if faulty_files:
                custom_write_to_textbox(
                state["messages"],
                "The following files could not be processed:\n"
                )  
                for file_name in faulty_files:
                    custom_write_to_textbox(state["messages"], f"  - {file_name}\n")  
        else:
            custom_show_error_message("Error", "Error reading data from the provided folder.")
            reset_state()

def plot_data():
    """Plots the spectral data loaded into the program state.
    This function retrieves the spectral data from the global state and plots it using Matplotlib. 
    The plot is embedded within the GUI window. If no data is currently loaded,an error message is
    displayed to the user.
    """
    if state["data"] is None:
        custom_show_error_message("Error", "Please load data first.\n")
        return
        
    if state["data"] and len(state["data"]) >= 2:
        x_data, y_data = state["data"]
    else:
        x_data, y_data = [], []
    reset_state("peaks")
    plt.close('all')
    fig, axis = plt.subplots()
    axis.plot(x_data, y_data, label='Intensity')
    axis.set_xlabel('Binding Energy (eV)')
    axis.set_ylabel('Intensity (arbitrary units)')
    axis.set_title('Photoionization Spectrum')
    axis.legend()

    if state["canvas"]:
        state["canvas"].get_tk_widget().destroy()
    state["canvas"] = FigureCanvasTkAgg(fig,
    master=state["window"])
    state["canvas"].draw()
    state["canvas"].get_tk_widget().pack(side=guilib.TOP, fill=tk.BOTH, expand=1)
    custom_write_to_textbox(state["messages"], "Data plotted successfully.\n")

def fit_line(point1, point2):
    """Fits a straight line through the given points using least squares regression.
    Parameters:
    - points (list): A list of (x, y) points on the plot through which the line is to be fit.
    Returns:
    - tuple: A tuple (slope, intercept) representing the line's equation: y = slope * x + intercept
    """
    slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
    intercept = point1[1] - slope * point1[0]
    custom_write_to_textbox(state["messages"],
    f"\nThe slope is {slope} and the intercept is {intercept}.")
    return slope, intercept

def get_two_points():
    """Initiates the process to let the user select two points on the plot.
    This function prepares the program state for capturing two user-selected points on the plot. 
    It sets up an event listener to detect mouse clicks on the plot, allowing the user to select 
    two points. These points are typically used to fit a linear background or select intervals for
    calculating intensity.
    """
    points = []
    def onclick(event):
        if event.xdata is None or event.ydata is None:
            custom_write_to_textbox(
            state["messages"],
            "\nSelected point is outside the plotting area. Please try again."
            )
            return
            
        if state["data"] and len(state["data"]) >= 2:
            x_data, y_data = state["data"]
        else:
            x_data, y_data = [], []
        nearest_index = np.argmin(np.abs(x_data - event.xdata))
        if (x_data is not None and y_data is not None and #fixing unsubscriptable possibility
        isinstance(x_data, (list, np.ndarray)) and
        isinstance(y_data, (list, np.ndarray))):
            nearest_point = (x_data[nearest_index], y_data[nearest_index])
            tolerance = 0.05 * max(y_data)
      
        if abs(nearest_point[1] - event.ydata) > tolerance:
            custom_write_to_textbox(
            state["messages"],
            "\nSelected point is not on the line. Please try again."
            )
            return

        if not points or (points and points[-1] != nearest_point):
            points.append(nearest_point)
            custom_write_to_textbox(state["messages"], f"\nYou selected: {nearest_point}")
        
        if len(points) == 2:
            state["canvas"].mpl_disconnect(state["callback_id"])

    if state["callback_id"]:
        state["canvas"].mpl_disconnect(state["callback_id"])
        
    state["callback_id"] = state["canvas"].mpl_connect('button_press_event', onclick)
    
    while len(points) < 2:
        state["window"].update_idletasks()
        state["window"].update()
    return points

def remove_background():
    """Removes the linear background from the loaded spectral data.
    This function prompts the user to select two points on the plot to fit a linear background.
    The background is then subtracted from the loaded data to provide a baseline-corrected spectrum.
    """
    if state["data"] is None or state["canvas"] is None:
        custom_show_error_message("Error", "Please load and plot data first.\n")
        return
        
    reset_state("peaks")
    custom_write_to_textbox(state["messages"],
    "Please select two points on the plot for background removal.\n")
    points = get_two_points()
    
    if len(points) != 2:
        custom_show_error_message("Error", "Failed to select two points. Please try again.\n")
        return
        
    slope, intercept = fit_line(points[0], points[1])
    if state["data"] and len(state["data"]) >= 2:
        x_data, y_data = state["data"]
    else:
        x_data, y_data = [], []
    y_corrected = y_data - (slope * x_data + intercept)
    state["data"] = (x_data, y_corrected)
    plot_data()
    custom_show_info_message("Info", "Linear background removed successfully.\n")

def calculate_intensity():
    """Calculates the intensity of the spectral data.
    This function computes the intensity of the loaded spectral data based on the current state. 
    Results and any relevant messages are displayed in the messages box.
    """
    if state["data"] is None or state["canvas"] is None:
        custom_show_error_message("Error", "Please load and plot data first.\n")
        return
    custom_write_to_textbox(
    state["messages"],
    "Please select the interval on the plot to calculate intensity.\n"
    )
    points = get_two_points()
    if len(points) != 2:
        custom_show_error_message("Error", "Failed to select an interval. Please try again.\n")
        return
        
    if state["data"] and len(state["data"]) >= 2:
        x_data, y_data = state["data"]
    else:
        x_data, y_data = [], []
    if (x_data is not None and y_data is not None and #fixing unsubscriptable possibility
        isinstance(x_data, (list, np.ndarray)) and
        isinstance(y_data, (list, np.ndarray))):
        lower_bound = min(points[0][0], points[1][0])
        upper_bound = max(points[0][0], points[1][0])
        mask = (x_data >= lower_bound) & (x_data <= upper_bound)
        x_interval = x_data[mask]
        y_interval = y_data[mask]

    if len(x_interval) == 0 or len(y_interval) == 0:
        custom_show_info_message(
        "Info",
        "No data points in the selected interval. Please choose a different interval.\n"
        )
        return

    intensity = np.trapz(y_interval, x_interval)
    custom_write_to_textbox(state["messages"], f"Calculated Intensity: {intensity:.2f}\n")
    state["peaks"].append((x_interval, y_interval))
    
    fig, axis = plt.gcf(), plt.gca()
    axis.clear()
    axis.plot(x_data, y_data, label='Intensity')  
    for x_int, y_int in state["peaks"]:
        axis.fill_between(x_int, y_int, color='yellow', alpha=0.5)
    axis.set_xlabel('Binding Energy (eV)')
    axis.set_ylabel('Intensity (arbitrary units)')
    axis.set_title('Photoionization Spectrum')
    axis.legend(['Intensity', 'Peaks'], loc="upper right")
    fig.canvas.draw()

    if state["canvas"]:
        state["canvas"].get_tk_widget().destroy()
    state["canvas"] = FigureCanvasTkAgg(fig, master=state["window"])
    state["canvas"].draw()
    state["canvas"].get_tk_widget().pack(side=guilib.TOP, fill=tk.BOTH, expand=1)
    custom_show_info_message("Info", "Intensity calculated and highlighted successfully.\n")

def save_figure():
    """Saves the currently displayed plot to a user-specified file.
    This function prompts the user to select a location and filename to save the current plot.
    The plot is then saved to the specified file in a suitable format(default is png).
    """
    if state["data"] is None:
        custom_show_error_message("Error", "Please load and plot data first.\n")
        return
        
    file_path = guilib.open_save_dialog("Save your file")
    if not file_path:
        custom_show_error_message("Error", "Failed to select a save location.\n")
        return
        
    if not file_path.lower().endswith(".png"):
        file_path += ".png"
    fig = state["canvas"].figure
    fig.savefig(file_path, format='png')
    custom_show_info_message("Info", f"Figure saved successfully to {file_path}.\n")
    
def close_app():
    """Handles the event when the user wishes to close the application.
    This function ensures that all necessary resources are released and any final actions are 
    performed before the application is closed. It then terminates the GUI event loop 
    and closes the application window.
    """
    state["window"].destroy()
    plt.close('all')
    
def main():
    """Main function to start the GUI application. 
    It initializes the GUI window and its components.
    """
    window = guilib.create_window("Spectral Matters Analyzer")
    state["window"] = window
    window.protocol("WM_DELETE_WINDOW", close_app)
    
    frame_left = guilib.create_frame(window)
    guilib.create_button(frame_left, "Load Data", load_data)
    guilib.create_button(frame_left, "Plot Data", plot_data)
    guilib.create_button(frame_left, "Remove Linear Background", remove_background)
    guilib.create_button(frame_left, "Calculate Intensities", calculate_intensity)
    guilib.create_button(frame_left, "Save Figure", save_figure)
    
    frame_right = guilib.create_frame(state["window"])
    state["messages"] = guilib.create_textbox(frame_right)
    guilib.start()

if __name__ == "__main__":
    main()
    
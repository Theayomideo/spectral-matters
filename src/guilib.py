"""
guilib - simple user interface library

@author Mika Oja, University of Oulu

This module is a collection of functions that students can use to implement a
simpe user interface that uses matplotlib to draw figures. The library makes a
lot of relatively sane assumptions so that students don't need to learn an
entire user interface library or study one's details. This may result in some
limitations regarding what can be implemented.

The library is basically a wrapper around TkInter that comes with Python. More
information here:

https://docs.python.org/3/library/tk.html

One of the most notable limitations is that while Tk will take care of most of
the widget placement (based on which frames they are in), the figure and
textbox sizes will be defined statically. Their dimensions will therefore
dictate what the interface will look like. If you want to make your interface
look neater, try to adjust the sizes of these components.

The main program of this module contains a small example that gives a some
directions about how to create basic widgets with this library.

"""

import tkinter as tk
from tkinter.ttk import Separator
from tkinter import messagebox, filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("TkAgg")

LEFT = tk.LEFT
RIGHT = tk.RIGHT
TOP = tk.TOP
BOTTOM = tk.BOTTOM

def create_window(title):
    """
    Creates a window for the user interface. The window is the root for
    everything else. This function needs to be called before any of the other
    functions can be used.

    :param str title: window title
    :return: returns the created window object
    """

    # we're using a global variable so that start and quit functions can be 
    # called without arguments
    global window
    window = tk.Tk()
    window.wm_title(title)
    return window

def create_frame(host, side=LEFT):
    """
    Creates a frame where other widgets can be placed. Frames can be used to
    divide the interface into segments that are easier to handle. They are also
    needed if widgets are to be placed along more than one axis.
    
    Frames can be placed inside the window, or inside other frames. The first
    argument of the function must therefore be either a window object or a
    frame object. The second argument influences where the frame will be placed
    inside its container. All components are packed against a wall - they form
    a stack of sorts. For instance, if two frames are packed against the top
    border, the frame that was packed first will be topmost, and the other
    will be below it.
    
    :param widget host: frame or window that will host the frame
    :param str side: which border of the host this frame is packed against
    :return: returns the created frame object
    """

    frame = tk.Frame(host)
    frame.pack(side=side, anchor="n")
    return frame

def create_button(frame, label, handler):
    """
    Creates a button that the user can click. Buttons work through handler
    functions. There must be a function in your code that is called whenever
    the user presses the button. This function doesn't receive any arguments.
    The function needs to be given to this function as its handler argument.
    E.g.:
    
    def donkey_button_handler():
        # something happens
        
    create_button(frame, "donkey", donkey_button_handler)

    Buttons are always packed against the top border of their frame which means
    they will be stacked on top of each other. If you want to pack them in a
    different way, you can always use this function as an example and write
    your own. 
    
    :param widget frame: frame that will host the buttons
    :param str label: text on the button
    :param function handler: function that is called when the button is pressed
    :return: returns the created button object
    """

    button = tk.Button(frame, text=label, command=handler)
    button.pack(side=tk.TOP, fill=tk.BOTH)
    return button

def create_figure(frame, mouse_handler, width, height):
    """
    Creates a figure and a canvas that will contain it. This function can be
    used to include a matplotlib figure inside the user inteface. The figure
    is displayed as a panel instead of a separate window. You can learn about
    how to handle the figure itself from matplotlib's documentation:
    
    https://matplotlib.org/api/figure_api.html
    https://matplotlib.org/api/axes_api.html

    This function also needs to receive a handler function that will be called
    whenever the user clicks the figure with the mouse. This works similarly to
    button handlers but the handler must have one parameter. This parameter is
    given an object from matplotlib that contains information about the mouse
    click. Useful information contained in this object includes xdata and ydata
    which are the axis values in the clicked position, and button that tells
    which mouse button was clicked (1 = left, 2 = middle, 3 = right). More
    info:
    
    http://matplotlib.org/api/backend_bases_api.html#matplotlib.backend_bases.MouseEvent

    The figure's width and height are given as pixels.

    :param widget frame: frame to host the figure
    :param function mouse_handler: function that will be called for clicks
    :param int width: figure width as pixels
    :param int height: figure height as pixels
    :return: canvas object, figure object, axes object
    """

    figure = Figure(figsize=(width / 100, height / 100), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP)
    canvas.mpl_connect("button_press_event", mouse_handler)
    subplot = figure.add_subplot()
    return canvas, figure, subplot

def create_textbox(frame, width=80, height=20):
    """
    Creates a textbox that can be written into much like terminal programs use
    print to output text. By default the textbox fills all available space in
    its frame. More specifically, this function creates a frame that contains
    the actual textbox, and a vertical scrollbar that's attached to it. 
    However, the frame and scrollbar objects are not returned, only the
    textbox itself.

    :param widget frame: frame to host the textbox
    :param int width: box width as characters
    :param int height: box height as rows
    :return: textbox object
    """

    boxframe = create_frame(frame, tk.TOP)
    scrollbar = tk.Scrollbar(boxframe)
    box = tk.Text(boxframe, height=height, width=width, yscrollcommand=scrollbar.set)
    box.configure(state="disabled")
    box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar.configure(command=box.yview)
    return box

def write_to_textbox(box, content, clear=False):
    """
    Writes a line of text into the selected textbox. The box can also be
    cleared before writing by setting the optional clear argument to True.

    :param widget box: textbox object to write to
    :param str content: text to write
    :param bool clear: should the box be cleared first
    """

    box.configure(state="normal")
    if clear:
        try:
            box.delete(1.0, tk.END)
        except tk.TclError:
            pass
    box.insert(tk.INSERT, content + "\n")
    box.configure(state="disabled")

def create_listbox(frame, width=80, height=20):
    """
    Creates a listbox. Unlike textboxes, the rows inside a listbox are separate
    entities. This means they can be clicked with the mouse, and can be removed
    and inserted individually.

    :param widget frame: host frame for the listbox
    :param int width: box width as characters
    :param int height: box height as rows
    :return: listbox object
    """

    boxframe = create_frame(frame, tk.TOP)
    scrollbar = tk.Scrollbar(boxframe)
    box = tk.Listbox(boxframe,
        height=height,
        width=width,
        yscrollcommand=scrollbar.set
    )
    box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar.configure(command=box.yview)
    return box

def add_list_row(box, content, place=tk.END):
    """
    Adds a textrow to a listbox. Place can be given as an optional argument
    which inserts the row into the selected spot. If place is not given, the
    new row will be appended to the end.

    :param widget box: listbox to add the row to
    :param str content: contents of the row
    :param int place: place in the list for insertion (optional)
    """

    box.insert(place, content)

def remove_list_row(box, index):
    """
    Removes the selected row from a listbox. Row is chosen with an index.

    :param widget box: listbox to remove from
    :param int index: index of the row
    """

    box.delete(index)

def read_selected(box):
    """
    Reads which row in a listbox has been selected with the mouse. Returns the
    index and contents of the row. If no rows have been selected, returns two
    Nones.

    :param widget box: listbox to read from
    """

    selected = box.curselection()
    if selected:
        content = box.get(selected)
        return selected[0], content
    return None, None

def create_label(frame, text):
    """
    Creates a static label that can be used to display state information or
    give labels to components or frames. 

    :param widget frame: frame to host the label
    :param str label: text of the label
    :return: label object
    """

    label = tk.Label(frame, text=text)
    label.pack(side=tk.TOP, fill=tk.BOTH)
    return label

def update_label(label, text):
    """
    Updates the text of the given label.

    :param widget label: label to update 
    :param str label: new text
    """

    labal.configure(text=text)

def create_textfield(frame):
    """
    Creates a textfield where the user can write text. The contents of the
    field can be accessed with the read_field function.

    :param widget frame: frame to host the textfield
    :return: textfield object
    """

    field = tk.Entry(frame)
    field.pack(side=tk.TOP, fill=tk.BOTH)
    return field

def read_field(field):
    """
    Reads the contents of the selected textfield and returns it.

    :param widget field: textfield to read
    :return: contents as a string
    """

    return field.get()

def clear_field(field):
    """
    Clears the selected textfield.

    :param widget field: textfield to clear
    """

    field.delete(0, len(field.get()))

def write_field(field, content):
    """
    Writes to the selected textfield.

    :param widget field: textfield to write to
    :param str content: content to write
    """

    field.insert(0, content)

def create_horiz_separator(frame, margin=2):
    """
    Creates a horizontal separator that can be used e.g. to partition the UI
    more clear. The function's optional argument can be used to adjust how much
    margin is left on both sides of the separator.

    :param widget frame: frame to host the separator
    :param int margin: amount of margin as pixels
    """

    separator = Separator(frame, orient="horizontal")
    separator.pack(side=tk.TOP, fill=tk.BOTH, pady=margin)

def create_vert_separator(frame, margin=2):
    """
    Creates a vertical separator that can be used e.g. to partition the UI
    more clear. The function's optional argument can be used to adjust how much
    margin is left on both sides of the separator.

    :param widget frame: frame to host the separator
    :param int margin: amount of margin as pixels
    """

    separator = Separator(frame, orient="vertical")
    separator.pack(side=tk.TOP, fill=tk.BOTH, pady=margin)

def open_msg_window(title, message, error=False):
    """
    Opens a popup window with a message to the user. The window can be defined
    as an error message by setting the error parameter as True. This changes
    the icon displayed in the window. The window is given a title and a message
    to display.

    :param str title: window title
    :param str message: message to display
    :param bool error: determines window type (info or error)
    """

    if error:
        messagebox.showerror(title, message)
    else:
        messagebox.showinfo(title, message)

def open_folder_dialog(title, initial="."):
    """
    Opens a folder selection dialog. Useful for choosing a data folder. The
    dialog must be given a title, and it can also be given an initial folder
    which will be open in the dialog when it pops up. The initial folder
    defaults to the folder where the program was started in. The function
    returns the folder chosen by the user as a string.

    :param str title: folder dialog title
    :param str initial: path to initial folder
    :return: path of the chosen folder
    """

    path = filedialog.askdirectory(title=title, mustexist=True, initialdir=initial)
    return path

def open_file_dialog(title, initial="."):
    """
    Opens a file selection dialog. The dialog must be given a title, and it can
    also be given an initial folder which will be open in the dialog when it
    pops up. The initial folder defaults to the folder where the program was
    started in. The function returns the chosen file's path as a string.

    :param str title: file dialog title
    :param str initial: path to initial folder
    :return: path of the chosen file
    """

    path = filedialog.askopenfilename(title=title, initialdir=initial)
    return path

def open_save_dialog(title, initial="."):
    """
    Opens a file selection dialog. The dialog must be given a title, and it can
    also be given an initial folder which will be open in the dialog when it
    pops up. The initial folder defaults to the folder where the program was
    started in. The function returns the chosen file's path as a string. The
    dialog for saving is a bit different than the one for opening.

    :param str title: file dialog title
    :param str initial: path to initial folder
    :return: path of the chosen file
    """

    path = filedialog.asksaveasfilename(title=title, initialdir=initial)
    return path

def remove_component(component):
    """
    Removes a component from the inteface. Needed for temporary widgets.

    :param widget component: component to remove
    """

    try:
        component.destroy()
    except AttributeError:
        component.get_tk_widget().destroy()

def create_subwindow(title):
    """
    Creates a subwindow that can be customized. A subwindow works just like a
    frame, i.e. any other components can be placed inside it. A subwindow can
    be hidden and showed again with the show_subwindow and hide_subwindow
    functions. The subwindow will also hide itself if the user closes it.

    :param str title: subwindow title
    :return: created subwindow object
    """

    sub = tk.Toplevel()
    sub.title(title)
    sub.protocol("WM_DELETE_WINDOW", sub.withdraw)
    return sub

def show_subwindow(sub, title=None):
    """
    Shows the selected subwindow.

    :param object ali: subwindow to show
    """

    if title:
        sub.title(title)
    sub.deiconify()

def hide_subwindow(sub):
    """
    Hides the selected subwindow.

    :param object ali: subwindow to hide
    """

    sub.withdraw()

def start():
    """
    Starts the program. Call this once your interface setup is done.
    """

    window.mainloop()

def quit():
    """
    Exits the program and closes the window.
    """

    window.destroy()

if __name__ == "__main__":
    # Disabling two pylint warnings because it would complain about the test
    # code despite it being perfectly valid.
    # pylint: disable=missing-docstring,unused-argument

    # rare case of defining a function inside this block. This is because it is
    # only used for testing the library.
    def greet():
        name = read_field(namefield)
        job = read_field(jobfield)
        if name and job:
            message = "Hello {}, I head you're a {}.".format(name, job)
            write_to_textbox(labelbox, message)
        else:
            open_msg_window("Missing info",
                "You didn't give name and occupation",
                error=True
            )

    testwindow = create_window("O Hai!")
    topframe = create_frame(testwindow, TOP)
    bottomframe = create_frame(testwindow, TOP)
    buttonframe = create_frame(topframe, LEFT)
    inputframe = create_frame(topframe, LEFT)
    greetbutton = create_button(buttonframe, "greet", greet)
    quitbutton = create_button(buttonframe, "quit", quit)
    namelabel = create_label(inputframe, "Nimi:")
    namefield = create_textfield(inputframe)
    joblabel = create_label(inputframe, "Ammatti:")
    jobfield = create_textfield(inputframe)
    labelbox = create_textbox(bottomframe, 34, 20)
    start()

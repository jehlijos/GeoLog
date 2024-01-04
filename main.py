import sys
import tkinter as tk
from tkinter import Toplevel, Label, ttk
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from screeninfo import get_monitors
import sqlite3
import os
from tkcalendar import DateEntry
import locale
import struct

# this app works with names of Czech teritorial units.
# Kraj is a region, okres is a district, obec is a municipality

# Set the locale to Czech
locale.setlocale(locale.LC_TIME, 'cs_CZ')


def print_file_contents(filename):
    """
    Print the contents of the file to the console.

    Parameters:
    filename (str): The path to the file.

    Returns:
    None
    """
    try:
        # Open the file in read mode
        with open(filename, 'r') as file:
            # Read the contents of the file
            file_contents = file.read()

            # Print the contents to the console
            print(file_contents)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file '{filename}' does not exist.") from e
    except IOError as e:
        raise IOError(f"An error occurred while reading the file: {e}") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"An error occurred while decoding the file: {e}") from e


def get_screen_resolution() -> tuple[int, int] | tuple[None, None]:
    """
    Returns the screen resolution of the primary monitor.
    If the resolution cannot be obtained, it returns a default resolution of 1920x1080.
    """
    try:
        primary_monitor = get_monitors()[0]
        width = primary_monitor.width
        height = primary_monitor.height
        if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
            raise ValueError("Invalid screen resolution")
        return width, height
    except IndexError:
        # Return default resolution if no monitors are found
        return 1920, 1080
    except Exception as e:
        print(f'Error occurred while getting screen resolution: {e}')
        return None, None


def loading_screen(root):
    """
    Creates a loading screen.

    Parameters:
    root (tkinter.Tk): The root Tkinter window.

    Returns:
    tkinter.Toplevel: The loading window.
    """
    loading_window = Toplevel(root)
    loading_window.title("NAČÍTÁNÍ...")
    loading_window.geometry("500x200")
    loading_window.iconbitmap("files/ico.ico")

    custom_font_large = ("Raleway", 48)  # Specify the font family and size for the large text
    custom_font_small = ("Raleway", 16)  # Specify the font family and size for the small text

    # Large text label
    label_large = Label(loading_window, text="NAČÍTÁNÍ...", font=custom_font_large)
    label_large.pack(pady=10)

    # Small text label
    label_small = Label(loading_window, text="Dejte si kávičku, za chvíli bude hotovo :)", font=custom_font_small)
    label_small.pack(pady=10)

    return loading_window


def plot_geopackage(root, gpkg_paths, loading_window):
    """
    Plot GeoPackage files on a Matplotlib figure embedded in a Tkinter window.

    Parameters:
    root (tkinter.Tk): The root Tkinter window.
    gpkg_paths (list): A list of tuples containing the GeoPackage file paths and their corresponding colors.
    loading_window (tkinter.Toplevel): The loading window to be destroyed before plotting.

    Returns:
    None
    """
    # Create a Matplotlib figure and axis
    fig, ax = plt.subplots()

    for gpkg_path, color in gpkg_paths:
        # Read GeoPackage file using GeoPandas
        gdf = gpd.read_file(gpkg_path)

        # Plot only the borders of the GeoDataFrame on Matplotlib axis and color them
        gdf.boundary.plot(ax=ax, color=color)

    # Hide the axis
    ax.set_axis_off()

    # Create a FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Destroy the loading window once the shapefiles are loaded
    loading_window.destroy()


def plot_geopackage_selection(root, gpkg_paths, loading_window, selected_nazev=None):
    """
    Plot GeoPackage files on a Matplotlib figure embedded in a Tkinter window.

    Parameters:
    root (tkinter.Tk): The root Tkinter window.
    gpkg_paths (list): A list of tuples containing the GeoPackage file paths and their corresponding colors.
    loading_window (tkinter.Toplevel): The loading window to be destroyed before plotting.
    selected_nazev (str): The selected nazev from the combobox.

    Returns:
    None
    """
    # Create a Matplotlib figure and axis
    loading_window = loading_screen(root)
    root.update()

    fig, ax = plt.subplots()

    # Read GeoPackage files and store them in a dictionary
    gpkg_data = {}
    column_mapping = {
        "geodata/kraje.shp": "nazev",
        "geodata/okresy.shp": "Název_kra",
        "geodata/obce_generalized.shp": "nazev_kraj"
    }
    # Get the necessary GeoPackage files based on the selected region
    necessary_gpkg_paths = []
    for gpkg_path, color in gpkg_paths:
        if gpkg_path in column_mapping:
            necessary_gpkg_paths.append((gpkg_path, color))

    for gpkg_path, color in necessary_gpkg_paths:
        gpkg_data[gpkg_path] = gpd.read_file(gpkg_path)

    # Dictionary mapping shapefile paths to the corresponding column names for filtering

    for gpkg_path, color in necessary_gpkg_paths:
        gdf = gpkg_data[gpkg_path]

        # Check if the shapefile path is in the column_mapping dictionary
        if gpkg_path in column_mapping:
            column_name = column_mapping[gpkg_path]

            # Check if the column exists in the GeoDataFrame
            if column_name in gdf.columns:
                # Filter GeoDataFrame based on the selected value in the corresponding column
                if selected_nazev is not None:
                    gdf = gdf[gdf[column_name] == selected_nazev]

                # Plot only the borders of the GeoDataFrame on Matplotlib axis and color them
                gdf.boundary.plot(ax=ax, color=color)

    ax.set_axis_off()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    loading_window.destroy()


def main():
    # prints the contents of the file to the console
    print_file_contents("files/console_sign.txt")
    screen_width, screen_height = get_screen_resolution()
    # Create a Tkinter window with map
    root = tk.Tk()
    root.geometry(f"{(screen_width - 100)}x{(screen_height - 100)}")
    root.title("GeoLog")
    root.iconbitmap("files/ico.ico")
    root.update()

    def quit_app():
        """
        Quit the application upon clicking on X.
        """
        cursor.close()
        root.quit()
        root2.quit()
        sys.exit()

    # Declare roots as a global variables so that they can be destroyed later
    global root3
    root3 = None
    global adduserpanelroot
    adduserpanelroot = None
    global removeuserpanelroot
    removeuserpanelroot = None
    global add_obec_root
    add_obec_root = None
    global remove_obec_root
    remove_obec_root = None

    # Declare combo_var and user as a global variable so that it can be accessed in other functions
    global combo_var_user
    global user
    global combo_var_REMuser
    global user_to_remove
    global combo_var_okresyADD
    global combo_var_krajeADD
    global conn
    global cursor
    combo_var_krajeADD = tk.StringVar()
    combo_var_okresyADD = tk.StringVar()
    combo_var_REMuser = tk.StringVar()

    user = "---"
    # Connect to the SQLite database
    DB_directory = 'database'
    conn = sqlite3.connect(os.path.join(DB_directory, 'users.db'))
    cursor = conn.cursor()

    # Specify the paths to your GeoPackage files and their corresponding colors
    kraje_shp_path = "geodata/kraje.shp"
    okresy_shp_path = "geodata/okresy.shp"
    obce_shp_path = "geodata/obce_generalized.shp"
    gpkg_paths = [
        (kraje_shp_path, 'blue'),
        (okresy_shp_path, 'green'),
        (obce_shp_path, 'gray')
    ]
    gpkg_paths_no_kraje = [
        (okresy_shp_path, 'green'),
        (obce_shp_path, 'gray')
    ]

    # Read GeoPackage file using GeoPandas
    kraje_shp = gpd.read_file(kraje_shp_path)
    okresy_shp = gpd.read_file(okresy_shp_path)
    obce_shp = gpd.read_file(obce_shp_path)
    # Display loading screen
    loading_window = loading_screen(root)
    root.update()

    # Plot "kraje.shp" first and then overlay "okresy.shp" on top
    plot_geopackage(root, gpkg_paths[::-1], loading_window)

    ######################### SETTINGS PANEL #########################
    root2 = tk.Toplevel(root)
    root2.geometry(f"{(int(screen_width * 0.25))}x{(int(screen_height * 0.45))}")
    root2.title("GeoLog - nastavení")
    root2.iconbitmap("files/ico.ico")
    root2.resizable(False, False)

    # kraj selection
    desc_font = ("Raleway", 10)  # Specify the font family and size for the description
    label = Label(root2, text="Přibliž na kraj:", font=desc_font)
    label.pack(pady=1)

    combo_var_kraje = tk.StringVar(root2)
    combo_var_kraje.set("--vyber kraj--")  # Default text in the combobox

    kraje_nazvy = kraje_shp['nazev'].unique()
    kraje_nazvy = ['Celá ČR'] + list(kraje_nazvy)

    # Enclose each 'nazev' value in double quotes
    quoted_kraje_nazvy = ['{}'.format(nazev) for nazev in kraje_nazvy]
    # Create a combobox with the list of  kraje names
    combo_box_kraje = ttk.Combobox(root2, textvariable=combo_var_kraje, values=quoted_kraje_nazvy)
    combo_box_kraje.pack(pady=20)

    # okresy selection (initially hidden)
    label = Label(root2, text="Přibliž na okres:", font=desc_font)
    label.pack(pady=1)  # show description

    # Create a combobox with the list of  okresy names
    combo_var_okresy = tk.StringVar(root2)
    combo_var_okresy.set("--vyber okres--")  # Default text in the combobox

    okresy_nazvy = ["Celý kraj"]  # You need to provide the actual list of okresy names

    # filling the combobox with okresy names
    quoted_okresy_nazvy = ['{}'.format(nazev) for nazev in okresy_nazvy]
    combo_box_okresy = ttk.Combobox(root2, textvariable=combo_var_okresy, values=quoted_okresy_nazvy, state="disabled")
    combo_box_okresy.pack(pady=20)

    selected_nazev_kraj = None

    def update_plot(event):
        """
        Update the plot based on the selected value in the combobox.
        Update the second combobox based on the selected value in the first combobox.
        """
        global selected_nazev_kraj
        global okresy_nazvy

        selected_nazev_kraj = combo_var_kraje.get()

        # Check if "Celá ČR" is selected
        if selected_nazev_kraj == "Celá ČR":
            # Destroy previous canvas widget
            for widget in root.winfo_children():
                if isinstance(widget, tk.Widget):
                    widget.destroy()
            plot_geopackage(root, gpkg_paths[::-1], loading_window)
            root.update()

            # Disable and reset the second combobox
            combo_box_okresy.set("--vyber okres--")
            combo_box_okresy['state'] = 'disabled'

            # Set okresy_nazvy to None when "Celá ČR" is selected
            okresy_nazvy = None
        else:
            # Enable the second combobox
            combo_box_okresy['state'] = 'readonly'

            # Continue with the previous logic for other selections
            for widget in root.winfo_children():
                if isinstance(widget, tk.Widget):
                    widget.destroy()
            okresy_nazvy = list(okresy_shp[okresy_shp['Název_kra'] == selected_nazev_kraj]['Název_okr'])
            plot_geopackage_selection(root, gpkg_paths[::-1], loading_window, selected_nazev_kraj)
            combo_box_okresy['values'] = okresy_nazvy
            combo_box_okresy.set('--vyber okres--')  # Reset the selection
            root.update()

    def plot_geopackage_selection_okr(root, gpkg_paths, loading_window, selected_nazev=None):
        """
        Plot GeoPackage files on a Matplotlib figure embedded in a Tkinter window.
        This modification only choses okresy.shp selected border and obce_generalized.shp
        Kraje are not plotted

        Parameters:
        root (tkinter.Tk): The root Tkinter window.
        gpkg_paths (list): A list of tuples containing the GeoPackage file paths and their corresponding colors.
        loading_window (tkinter.Toplevel): The loading window to be destroyed before plotting.
        selected_nazev (str): The selected nazev from the combobox.

        Returns:
        None
        """
        # Create a Matplotlib figure and axis
        loading_window = loading_screen(root)
        root.update()

        fig, ax = plt.subplots()

        # Read GeoPackage files and store them in a dictionary
        gpkg_data = {}
        column_mapping = {
            "geodata/okresy.shp": "Název_okr",
            "geodata/obce_generalized.shp": "nazev_okre"  # Updated mapping
        }
        # Get the necessary GeoPackage files based on the selected region
        necessary_gpkg_paths = []
        for gpkg_path, color in gpkg_paths:
            if gpkg_path in column_mapping:
                necessary_gpkg_paths.append((gpkg_path, color))

        for gpkg_path, color in necessary_gpkg_paths:
            gpkg_data[gpkg_path] = gpd.read_file(gpkg_path)

        # Dictionary mapping shapefile paths to the corresponding column names for filtering

        for gpkg_path, color in necessary_gpkg_paths:
            gdf = gpkg_data[gpkg_path]

            # Check if the shapefile path is in the column_mapping dictionary
            if gpkg_path in column_mapping:
                column_name = column_mapping[gpkg_path]

                # Check if the column exists in the GeoDataFrame
                if column_name in gdf.columns:
                    # Filter GeoDataFrame based on the selected value in the corresponding column
                    if selected_nazev is not None:
                        gdf = gdf[gdf[column_name] == selected_nazev]

                    # Plot only the borders of the GeoDataFrame on Matplotlib axis and color them
                    gdf.boundary.plot(ax=ax, color=color)

        ax.set_axis_off()

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        loading_window.destroy()

    def update_plot_okres(event):
        """
        Update the plot based on the selected value in the second combobox.
        """
        global selected_nazev_okres
        global okresy_nazvy

        selected_nazev_okres = combo_var_okresy.get()

        # Plot okres and obce
        for widget in root.winfo_children():
            if isinstance(widget, tk.Widget):
                widget.destroy()
        plot_geopackage_selection_okr(root, gpkg_paths_no_kraje[::-1], loading_window, selected_nazev_okres)
        root.update()

    # Bind the event to update_plot function for kraje/okresy combobox
    combo_box_kraje.bind("<<ComboboxSelected>>", update_plot)

    combo_box_okresy.bind("<<ComboboxSelected>>", update_plot_okres)

    def add_user():
        """
        Create a new table in the database with the name of the user.
        global user is set to the name of the user.
        close the adduserpanelroot and root3 window.
        enable buttons 1,2,3
        """
        global user
        global entryuser

        username = str(entryuser.get())
        # Check if username is empty
        if not username or ' ' in username:
            print("Neplatné jméno, nepoužívej mezery")
            labelusererr = Label(adduserpanelroot, text="Neplatné jméno, nepoužívej mezery", font=desc_font, fg="red")
            labelusererr.pack(pady=1)
            return

        # Check if username contains only alphanumeric characters
        if not username.isalnum():
            print("Neplatné jméno, nepoužívej mezery")
            labelusererr = Label(adduserpanelroot, text="Neplatné jméno, nepoužívej mezery", font=desc_font, fg="red")
            labelusererr.pack(pady=1)
            return

        # Check if username already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = cursor.fetchall()  # Returns a list of tables in the database = users
        if (username,) in existing_tables:
            print("uzivatel uz existuje")
            labelusererr = Label(adduserpanelroot, text="Uživatel již existuje", font=desc_font, fg="red")
            labelusererr.pack(pady=1)
            return

        print("uzivatel vytvoren: " + username)
        # Create a new table in the database with the name of the user
        cursor.execute("CREATE TABLE IF NOT EXISTS " + username + "(id INTEGER PRIMARY KEY, obecID VARCHAR(6), "
                                                                  "dat DATE)")
        user = username
        user_label.config(text="Uživatel:  " + user)

        # Enable buttons 1,2,3
        button1.config(state="normal")
        button2.config(state="normal")
        button3.config(state="normal")

        root3.destroy()
        adduserpanelroot.destroy()

    def adduserpanel():
        """
        Create a new window with a entry to enter a new user.
        """
        global adduserpanelroot
        global entryuser

        # Check if root already exists and destroy it if it does remove it
        if adduserpanelroot is not None:
            try:
                adduserpanelroot.destroy()
            except:
                pass
        adduserpanelroot = tk.Tk()
        adduserpanelroot.geometry(f"{(int(screen_width * 0.25))}x{(int(screen_height * 0.25))}")
        adduserpanelroot.title("GeoLog - nový uživatel")
        adduserpanelroot.iconbitmap("files/ico.ico")
        adduserpanelroot.update()

        # Text
        labeluser = Label(adduserpanelroot, text="Vlož jméno nového uživatele:", font=desc_font)
        labeluser.pack(pady=1)

        # user entry window
        entryuser = tk.Entry(adduserpanelroot, width=30)
        entryuser.pack(pady=20)

        # Confirm button
        button_adduser = tk.Button(adduserpanelroot, text="PŘIDAT", command=add_user, bg="light green", padx=10,
                                   pady=5,
                                   width=15)
        button_adduser.pack(padx=5)

        adduserpanelroot.protocol("WM_DELETE_WINDOW",
                                  adduserpanelroot.destroy)  # Destroy root3 when the user closes the window

    def existing_user_selected(event):
        """
        Update the global user variable and enable buttons 1,2,3.
        This function is bound to the <<ComboboxSelected>> event.
        """
        global user

        user = combo_var_user.get()
        user_label.config(text="Uživatel:  " + user)
        print("uzivatel zmenen: " + user)

        # Enable buttons 1,2,3
        button1.config(state="normal")
        button2.config(state="normal")
        button3.config(state="normal")

        root2.update()
        root3.destroy()

    def removeuser():
        """
        Remove the selected user from the database upon clicking the button.
        """
        global user_to_remove
        global user

        cursor.execute("DROP TABLE " + user_to_remove)
        print("uzivatel smazan: " + user_to_remove)
        user = "---"
        user_label.config(text="Uživatel:  " + user)

        button1.config(state="disabled")
        button2.config(state="disabled")
        button3.config(state="disabled")

        root3.destroy()
        removeuserpanelroot.destroy()

    def update_REMuser_var(event=None):
        """
        Update the global user_to_remove variable.
        This function is bound to the <<ComboboxSelected>> event.
        This will update the value to be removed, but will not remove it.
        Pushing the red button will remove the user.
        """
        global combo_var_REMuser
        global user_to_remove
        user_to_remove = combo_var_REMuser.get()

    def removeuserpanel():
        """
        Create a new window with a combobox to select a user.
        Selecting a user will update the global user_to_remove variable.
        Pushing the red button will remove the user.
        """
        global removeuserpanelroot
        global entryuser
        global combo_var_REMuser

        # Check if root already exists and destroy it if it does remove it
        if removeuserpanelroot is not None:
            try:
                removeuserpanelroot.destroy()
            except:
                pass
        # Window creation
        removeuserpanelroot = tk.Tk()
        removeuserpanelroot.geometry(f"{(int(screen_width * 0.25))}x{(int(screen_height * 0.25))}")
        removeuserpanelroot.title("GeoLog - vymaž uživatele")
        removeuserpanelroot.iconbitmap("files/ico.ico")
        removeuserpanelroot.update()
        # Text
        labeluser = Label(removeuserpanelroot, text="Vyber uživatele pro smazání:", font=desc_font)
        labeluser.pack(pady=1)

        # Combobox
        combo_var_REMuser = tk.StringVar(removeuserpanelroot)
        combo_var_REMuser.set("--vyber uživatele--")  # Default text in the combobox

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rem_tables = cursor.fetchall()  # Returns a list of tables in the database = users

        combo_box_REMuser = ttk.Combobox(removeuserpanelroot, textvariable=combo_var_REMuser, values=rem_tables)
        combo_box_REMuser.pack(pady=20)
        combo_box_REMuser.bind("<<ComboboxSelected>>", update_REMuser_var)

        # Text
        labeluser = Label(removeuserpanelroot, text="STISKNUTÍM TLAČÍTKA NÍŽE NEVRATNĚ \n SMAŽETE UŽIVATELSKÁ DATA",
                          font=desc_font)
        labeluser.pack(pady=1)

        # Button
        button_removeuser = tk.Button(removeuserpanelroot, text="Odeber uživatele", command=removeuser, bg="red",
                                      padx=10,
                                      pady=5,
                                      fg="white",
                                      width=15)
        button_removeuser.pack(padx=5)

        removeuserpanelroot.protocol("WM_DELETE_WINDOW", removeuserpanelroot.destroy)
        # Destroy removeuserpanelroot when the user closes the window

    def userpanel():
        """
        Create a new window with a combobox to select a user.
        """
        global root3
        global combo_var_user  # Add this line to declare combo_var_user as a global variable

        # Check if root3 already exists and destroy it if it does remove it
        if root3 is not None:
            try:
                root3.destroy()
            except:
                pass

        # Root3 is the window with the combobox to select a user
        root3 = tk.Tk()
        root3.geometry(f"{(int(screen_width * 0.25))}x{(int(screen_height * 0.25))}")
        root3.title("GeoLog - uživatelé")
        root3.iconbitmap("files/ico.ico")
        root3.update()

        # Text
        labeluser = Label(root3, text="Vyber uživatele:", font=desc_font)
        labeluser.pack(pady=1)

        # Combobox
        combo_var_user = tk.StringVar(root3)
        combo_var_user.set("--vyber uživatele--")  # Default text in the combobox

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()  # Returns a list of tables in the database = users

        combo_box_user = ttk.Combobox(root3, textvariable=combo_var_user, values=tables)
        combo_box_user.pack(pady=20)

        combo_box_user.bind("<<ComboboxSelected>>", existing_user_selected)  # Bind the event to update user

        # Buttons
        button_adduser = tk.Button(root3, text="Přidej uživatele", command=adduserpanel, bg="light green", padx=10,
                                   pady=5,
                                   width=15)

        button_removeuser = tk.Button(root3, text="Odeber uživatele", command=removeuserpanel, bg="orange", padx=10,
                                      pady=5,
                                      width=15)

        button_adduser.pack(padx=5)
        button_removeuser.pack(padx=5)

        root3.protocol("WM_DELETE_WINDOW", root3.destroy)  # Destroy root3 when the user closes the window

    # Separator between buttons
    separator = ttk.Separator(root2, orient="horizontal")
    separator.pack(fill="x", pady=10)

    # Button to open user panel
    user_button = ttk.Button(root2, text="Vyber uživatele", command=userpanel)
    user_button.pack()

    user_label = ttk.Label(root2, text="Uživatel:  " + user)
    user_label.pack()

    # Separator between buttons
    separator = ttk.Separator(root2, orient="horizontal")
    separator.pack(fill="x", pady=10)

    def add_obec_window():
        """
        Add a new window with a combobox to select a kraj.
        Upon selecting a kraj, the second combobox will be enabled and populated with okresy.
        Upon selecting an okres, the third combobox will be enabled and populated with obce.
        """
        global add_obec_root
        global combo_var_okresyADD
        global combo_var_krajeADD
        global quoted_okresyADD_nazvy
        global quoted_obecADD_nazvy
        global combo_var_obecADD

        # Check if root already exists and destroy it if it does remove it
        if add_obec_root is not None:
            try:
                add_obec_root.destroy()
            except:
                pass
            # Window creation
        add_obec_root = tk.Tk()
        add_obec_root.geometry(f"{(int(screen_width * 0.25))}x{(int(screen_height * 0.48))}")
        add_obec_root.title("GeoLog - přidej obec")
        add_obec_root.iconbitmap("files/ico.ico")
        add_obec_root.update()

        # COMBOBOXES CREATION
        # kraj selection
        desc_font = ("Raleway", 10)  # Specify the font family and size for the description
        label = Label(add_obec_root, text="Vyber kraj:", font=desc_font)
        label.pack(pady=1)

        combo_var_krajeADD = tk.StringVar(add_obec_root)
        combo_var_krajeADD.set("--vyber kraj--")  # Default text in the combobox

        krajeADD_nazvy = kraje_shp['nazev'].unique()
        krajeADD_nazvy = ['Celá ČR'] + list(krajeADD_nazvy)

        # Enclose each 'nazev' value in double quotes
        quoted_krajeADD_nazvy = ['{}'.format(nazev) for nazev in krajeADD_nazvy]
        combo_box_krajeADD = ttk.Combobox(add_obec_root, textvariable=combo_var_krajeADD, values=quoted_krajeADD_nazvy)
        combo_box_krajeADD.pack(pady=20)

        # okresy selection (initially hidden)
        label = Label(add_obec_root, text="Vyber okres:", font=desc_font)
        label.pack(pady=1)  # show description

        combo_var_okresyADD = tk.StringVar(add_obec_root)
        combo_var_okresyADD.set("--vyber okres--")  # Default text in the combobox

        okresyADD_nazvy = ["Celý kraj"]  # You need to provide the actual list of okresy names

        quoted_okresyADD_nazvy = ['{}'.format(nazev) for nazev in okresyADD_nazvy]
        combo_box_okresyADD = ttk.Combobox(add_obec_root, textvariable=combo_var_okresyADD,
                                           values=quoted_okresyADD_nazvy, state="disabled")
        combo_box_okresyADD.pack(pady=20)

        label = Label(add_obec_root, text="Vyber obec:", font=desc_font)
        label.pack(pady=1)  # show description

        # obec selection (initially hidden)
        combo_var_obecADD = tk.StringVar(add_obec_root)
        combo_var_obecADD.set("--vyber obec--")  # Default text in the combobox

        obecADD_nazvy = []

        quoted_obecADD_nazvy = ['{}'.format(nazev) for nazev in obecADD_nazvy]
        combo_box_obecADD = ttk.Combobox(add_obec_root, textvariable=combo_var_obecADD,
                                         values=quoted_obecADD_nazvy, state="disabled")
        combo_box_obecADD.pack(pady=20)

        label = Label(add_obec_root, text="Vyber datum:", font=desc_font)
        label.pack(pady=1)  # show description

        # Calendar widget for date selection with Czech lagnuage and format
        cal = DateEntry(add_obec_root, locale='cs_CZ', date_pattern='dd-mm-yyyy', selectmode='day')
        cal.pack(pady=20)

        def IMPORTobec():
            """
            Insert the selected obec into the database upon button click.
            """
            global ADDokres
            global ADDobec

            selected_date = cal.get()
            sqldate = selected_date[6:10] + "-" + selected_date[3:5] + "-" + selected_date[0:2]
            # Get the obecID of the selected obec and okres
            OBECID = \
                obce_shp[(obce_shp['nazev_okre'] == ADDokres) & (obce_shp['nazev_obce'] == ADDobec)]['kod_obce'].iloc[0]
            # Insert the obecID and date into the database

            obecIDs = cursor.execute("SELECT obecID FROM " + user)
            obecIDs = obecIDs.fetchall()

            # Check if obec is already in the database
            if OBECID in obecIDs:
                print("obec uz je zaznamenana")
                return

            # Insert the obecID and date into the database
            cursor.execute("INSERT INTO " + user + " (obecID, dat) VALUES (?, ?)", (str(OBECID), sqldate))
            conn.commit()
            print("obec pridana: " + ADDobec + "(" + ADDokres + ") -" + selected_date)

        ADDbutton = tk.Button(add_obec_root, text="Přidej obec", command=IMPORTobec, bg="light green", padx=10,
                              pady=5,
                              width=15)
        ADDbutton.pack(padx=5)
        ADDbutton.config(state="disabled")

        def ADDkraje(event):
            """
            Update the second combobox based on the selected value in the first combobox.
            """
            global quoted_okresyADD_nazvy
            global combo_var_krajeADD

            ADDkraj = combo_var_krajeADD.get()

            # Check if "Celá ČR" is selected
            if ADDkraj == "Celá ČR":
                combo_box_okresyADD.set("--vyber okres--")
                combo_box_okresyADD['state'] = 'disabled'
                return
            # Enable the second combobox, fill it wih okresy and reset the selection
            quoted_okresyADD_nazvy = list(okresy_shp[okresy_shp['Název_kra'] == ADDkraj]['Název_okr'])
            combo_box_okresyADD['values'] = quoted_okresyADD_nazvy
            combo_box_okresyADD.set('--vyber okres--')
            combo_box_okresyADD['state'] = 'readonly'

        def ADDokresy(event):
            """
            Update the third combobox based on the selected value in the second combobox.
            """
            global combo_var_okresyADD
            global quoted_obecADD_nazvy
            global ADDokres

            ADDokres = combo_var_okresyADD.get()
            combo_box_obecADD.set("--vyber obec--")
            combo_box_obecADD['state'] = 'enabled'  # Enable the third combobox
            quoted_obecADD_nazvy = list(obce_shp[obce_shp['nazev_okre'] == ADDokres]['nazev_obce'])
            combo_box_obecADD['values'] = quoted_obecADD_nazvy

        def ADDobec(event):
            """
            Update the global variable ADDobec based on the selected value in the third combobox.
            """
            global combo_var_obecADD
            global ADDobec
            ADDobec = combo_var_obecADD.get()
            ADDbutton.config(state="normal")

        combo_box_krajeADD.bind("<<ComboboxSelected>>", ADDkraje)
        combo_box_okresyADD.bind("<<ComboboxSelected>>", ADDokresy)
        combo_box_obecADD.bind("<<ComboboxSelected>>", ADDobec)

        add_obec_root.protocol("WM_DELETE_WINDOW", add_obec_root.destroy)
        # Destroy removeuserpanelroot when the user closes the window

    def stopar_window():
        print("stopar window soon to be added")

    def remove_obec_window():
        """
        Add a new window with a combobox to remove obec.
        Upon selecting an obec, the global variable REMstring will be updated.
        Pushing the red button will remove the obec.
        """
        global remove_obec_root
        global combo_var_REMobec
        global REMstring
        REMstring = None

        # Check if root already exists
        if remove_obec_root is not None:
            try:
                remove_obec_root.destroy()
            except:
                pass
        # Window creation
        remove_obec_root = tk.Tk()
        remove_obec_root.geometry(f"{(int(screen_width * 0.25))}x{(int(screen_height * 0.25))}")
        remove_obec_root.title("GeoLog - odeber obec")
        remove_obec_root.iconbitmap("files/ico.ico")
        remove_obec_root.update()

        # Get the obecIDs from the database
        obecIDs = cursor.execute("SELECT obecID FROM " + user)
        obecIDs = obecIDs.fetchall()
        obecIDs = [int(item[0]) for item in obecIDs]

        # Get the obec names from shapefile
        obecnames_andIDs = obce_shp[obce_shp['kod_obce'].isin(obecIDs)][['nazev_obce', 'kod_obce']].values.tolist()
        # Create a list of strings in the format "nazev_obce(kod_obce)"
        obecnames_andIDs_str = [f'{item[0]}({item[1]})' for item in obecnames_andIDs]

        # Text
        label = Label(remove_obec_root, text="Vyber obec pro smazání:", font=desc_font)
        label.pack(pady=1)

        # Combobox
        combo_var_REMobec = tk.StringVar(remove_obec_root)

        combo_box_REMobec = ttk.Combobox(remove_obec_root, textvariable=combo_var_REMobec, values=obecnames_andIDs_str)
        combo_box_REMobec.pack(pady=20)
        combo_var_REMobec.set("--vyber obec--")
        combo_box_REMobec['state'] = 'readonly'

        def REMcombobox(event):  # Update the global variable REMstring with the selected obecID

            global combo_var_REMobec
            global REMstring
            REMstring = combo_var_REMobec.get()
            REMstring = REMstring.split("(")
            REMstring = REMstring[1].split(")")
            REMstring = int(REMstring[0])

        def REMbutton():
            """
            Remove the selected obec from the database upon button click.
            """
            global REMstring
            global user
            global conn
            global cursor
            global combo_var_REMobec

            if REMstring is None:
                return

            dbstring = "DELETE FROM " + user + " WHERE obecID = " + str(REMstring) + " ;"
            cursor.execute(dbstring)
            conn.commit()
            print("obec odebrana: " + str(REMstring))

            # UPDATE THE COMBOBOX WITH THE REMOVED OBEC
            obecIDs = cursor.execute("SELECT obecID FROM " + user)
            obecIDs = obecIDs.fetchall()
            obecIDs = [int(item[0]) for item in obecIDs]

            # Get the obec names from the database
            obecnames_andIDs = obce_shp[obce_shp['kod_obce'].isin(obecIDs)][['nazev_obce', 'kod_obce']].values.tolist()
            # Create a list of strings in the format "nazev_obce(kod_obce)"
            obecnames_andIDs_str = [f'{item[0]}({item[1]})' for item in obecnames_andIDs]
            combo_box_REMobec['values'] = obecnames_andIDs_str
            combo_var_REMobec.set("--vyber obec--")

        # Text
        label = Label(remove_obec_root, text="TLAČÍTKEM NEVRATNĚ SMAŽETE \n VYBRANOU OBEC", font=desc_font)
        label.pack(pady=1)

        # Button
        button_REMobec = tk.Button(remove_obec_root, text="Odeber obec", command=REMbutton, bg="pink", padx=10,
                                   pady=5,
                                   width=15)
        button_REMobec.pack(padx=5)

        combo_box_REMobec.bind("<<ComboboxSelected>>", REMcombobox)

        remove_obec_root.protocol("WM_DELETE_WINDOW", remove_obec_root.destroy)

    # Create button to open add_obec_window
    button1 = tk.Button(root2, text="Přidej obec", command=add_obec_window, bg="green", padx=10, pady=5,
                        width=15, fg="white", state="disabled")

    # Create button to open stopar_window
    button2 = tk.Button(root2, text="Načti stopaře", command=stopar_window, bg="light green", padx=10,
                        pady=5, width=15, state="disabled")

    # Create button to open remove_obec_window
    button3 = tk.Button(root2, text="Odeber obec", command=remove_obec_window, bg="orange", padx=10, pady=5,
                        width=15, state="disabled")

    button1.pack(padx=5)
    button2.pack(padx=5)
    button3.pack(padx=5)

    # protocol for actually quiting the app upon clicking on X
    root2.protocol("WM_DELETE_WINDOW", quit_app)
    root.protocol("WM_DELETE_WINDOW", quit_app)
    root2.mainloop()
    root.mainloop()


if __name__ == '__main__':
    main()

#	°¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦°
#	-                                  -
#	-    _      _     _ _ _            -
#	-   (_)    | |   | (_(_)           -
#	-    _  ___| |__ | |_ _  ___  ___  -
#	-   | |/ _ | '_ \| | | |/ _ \/ __| -
#	-   | |  __| | | | | | | (_) \__ \ -
#	-   | |\___|_| |_|_|_| |\___/|___/ -
#	-  _/ |             _/ |           -
#	- |__/             |__/            -
#	-                                  -
#	°¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦°

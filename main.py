import tkinter as tk
from tkinter import Toplevel, Label, ttk
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from screeninfo import get_monitors


def print_file_contents(filename):
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
    print_file_contents("files/console_sign.txt")
    screen_width, screen_height = get_screen_resolution()
    root = tk.Tk()
    root.geometry(f"{(screen_width - 100)}x{(screen_height - 100)}")
    root.title("GeoLog")
    root.iconbitmap("files/ico.ico")
    root.update()

    # Specify the paths to your GeoPackage files and their corresponding colors
    kraje_shp_path = "geodata/kraje.shp"
    gpkg_paths = [
        (kraje_shp_path, 'blue'),
        ("geodata/okresy.shp", 'green'),
        ("geodata/obce_generalized.shp", 'gray')
    ]

    # Read GeoPackage file using GeoPandas
    kraje_shp = gpd.read_file(kraje_shp_path)

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

    def update_plot(event):
        selected_nazev = combo_var.get()

        # Check if "Celá ČR" is selected
        if selected_nazev == "Celá ČR":
            # Destroy previous canvas widget
            for widget in root.winfo_children():
                if isinstance(widget, tk.Widget):
                    widget.destroy()
            plot_geopackage(root, gpkg_paths[::-1], loading_window)
            root.update()
        else:
            # Continue with the previous logic for other selections
            for widget in root.winfo_children():
                if isinstance(widget, tk.Widget):
                    widget.destroy()
            plot_geopackage_selection(root, gpkg_paths[::-1], loading_window, selected_nazev)
            root.update()

    # kraj selection
    desc_font = ("Raleway", 10)
    label = Label(root2, text="Přibliž na kraj:", font=desc_font)
    label.pack(pady=1)

    combo_var = tk.StringVar(root2)
    combo_var.set("--vyber kraj--")  # Default text in the combobox

    kraje_nazvy = kraje_shp['nazev'].unique()
    kraje_nazvy = ['Celá ČR'] + list(kraje_nazvy)

    # Enclose each 'nazev' value in double quotes
    quoted_kraje_nazvy = ['{}'.format(nazev) for nazev in kraje_nazvy]
    combo_box = ttk.Combobox(root2, textvariable=combo_var, values=quoted_kraje_nazvy)
    combo_box.pack(pady=20)
    combo_box.bind("<<ComboboxSelected>>", update_plot)

    root2.mainloop()
    root.mainloop()


if __name__ == '__main__':
    main()

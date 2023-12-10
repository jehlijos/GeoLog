import tkinter as tk
from tkinter import Toplevel, Label
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

    custom_font = ("Raleway", 48)  # Specify the font family and size

    label = Label(loading_window, text="NAČÍTÁNÍ...", font=custom_font)
    label.pack(pady=20)

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


def main():
    print_file_contents("files/console_sign.txt")
    screen_width, screen_height = get_screen_resolution()
    root = tk.Tk()
    root.geometry(f"{(screen_width - 200)}x{(screen_height - 200)}")
    root.title("GeoLog")
    root.iconbitmap("files/ico.ico")
    root.update()

    # Specify the paths to your GeoPackage files and their corresponding colors
    gpkg_paths = [
        ("geodata/kraje.shp", 'purple'),
        ("geodata/okresy.shp", 'blue'),
        ("geodata/obce_generalized.shp", 'gray')
    ]

    # Display loading screen
    loading_window = loading_screen(root)
    root.update()

    # Plot "kraje.shp" first and then overlay "okresy.shp" on top
    plot_geopackage(root, gpkg_paths[::-1], loading_window)

    root.mainloop()


if __name__ == '__main__':
    main()

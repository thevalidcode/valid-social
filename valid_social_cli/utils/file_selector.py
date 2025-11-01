from tkinter import Tk, filedialog
from typing import List, Optional, Union, Tuple


def select_file(
    title: str = "Select a file",
    file_types: Optional[List[Tuple[str, str]]] = None,
    multiple: bool = False
) -> Optional[Union[str, List[str]]]:
    """
    Opens a system file picker and returns the selected file path(s).

    Args:
        title (str): Title of the dialog window.
        file_types (list[tuple[str, str]] | None): List of tuples like
            [("Images", "*.png;*.jpg"), ("All", "*.*")]
        multiple (bool): Whether to allow selecting multiple files.

    Returns:
        str | list[str] | None: The selected file path(s), or None if cancelled.
    """

    if file_types is None:
        file_types = [
            ("Images & Videos", "*.png *.jpg *.jpeg *.webp *.gif *.mp4 *.mov *.avi *.mkv"),
            ("All Files", "*.*"),
        ]

    root = Tk()
    root.withdraw()  # Hide main window

    result: Optional[Union[str, List[str]]] = None  # Explicitly include None

    if multiple:
        file_paths = filedialog.askopenfilenames(
            title=title, filetypes=file_types)
        if file_paths:
            result = list(file_paths)
    else:
        file_path = filedialog.askopenfilename(
            title=title, filetypes=file_types)
        if file_path:
            result = file_path

    root.destroy()
    return result


import os
import shutil
from pathlib import Path

# Downloads folder location
DOWNLOADS_FOLDER = Path.home() / "Downloads"

# Set True to test without moving files.
# Change to False when you are ready to organize.
DRY_RUN = False

# Extension-to-folder mapping
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".xlsx": "Documents",
    ".xls": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".svg": "Images",

    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".mov": "Videos",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",

    # Code
    ".py": "Code",
    ".java": "Code",
    ".cpp": "Code",
    ".c": "Code",
    ".html": "Code",
    ".css": "Code",
    ".js": "Code"
}


def get_unique_path(destination):
    """Generate a new filename if one already exists."""

    if not destination.exists():
        return destination

    folder = destination.parent
    name = destination.stem
    extension = destination.suffix

    counter = 1

    while True:
        new_name = f"{name}_{counter}{extension}"
        new_path = folder / new_name

        if not new_path.exists():
            return new_path

        counter += 1


def organize_files():

    print("=" * 55)
    print("           AUTOMATIC FILE ORGANIZER")
    print("=" * 55)

    if not DOWNLOADS_FOLDER.exists():
        print("Downloads folder not found!")
        return

    moved = 0
    skipped = 0
    errors = 0

    try:
        with os.scandir(DOWNLOADS_FOLDER) as entries:

            for entry in entries:

                if not entry.is_file(follow_symlinks=False):
                    continue

                source = Path(entry.path)

                category = EXTENSION_MAP.get(
                    source.suffix.lower(), "Others"
                )

                destination_folder = DOWNLOADS_FOLDER / category

                try:
                    destination_folder.mkdir(
                        parents=True, exist_ok=True
                    )

                    destination = get_unique_path(
                        destination_folder / source.name
                    )

                    if DRY_RUN:
                        print(
                            f"[TEST] {source.name} -> {category}"
                        )
                    else:
                        shutil.move(str(source), str(destination))
                        print(
                            f"[MOVED] {source.name} -> {category}"
                        )

                    moved += 1

                except PermissionError:
                    print(f"[PERMISSION DENIED] {source.name}")
                    errors += 1

                except FileExistsError:
                    print(f"[FILE EXISTS] {source.name}")
                    skipped += 1

                except OSError as error:
                    print(f"[ERROR] {source.name}: {error}")
                    errors += 1

    except PermissionError:
        print("Cannot access the Downloads folder!")
        return

    print("\n" + "=" * 55)
    print("             EXECUTION SUMMARY")
    print("=" * 55)

    print("Files processed :", moved)
    print("Files skipped   :", skipped)
    print("Errors          :", errors)

    if DRY_RUN:
        print("\nDRY RUN: No files were moved.")
        print("Set DRY_RUN = False to organize files.")
    else:
        print("\nFile organization completed!")

    print("=" * 55)


if __name__ == "__main__":
    organize_files()

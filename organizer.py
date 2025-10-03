# organizer.py
from pathlib import Path
import shutil
import mimetypes

# map categories to extensions (lowercase, without dot)
CATEGORY_MAP = {
    "Images": {"jpg","jpeg","png","gif","bmp","svg","webp","heic","tiff"},
    "Videos": {"mp4","mkv","mov","avi","webm","flv","wmv"},
    "Documents": {"pdf","doc","docx","xls","xlsx","ppt","pptx","odt","ods","txt","rtf"},
    "Archives": {"zip","rar","7z","tar","gz","bz2","tar.gz","tgz"},
    "Audio": {"mp3","wav","aac","flac","ogg","m4a"},
    "Code": {"py","js","ts","java","c","cpp","cs","html","css","json","go","rs","rb"},
}

# Flatten allowed extensions for upload checking
ALLOWED_EXTENSIONS = set()
for s in CATEGORY_MAP.values():
    ALLOWED_EXTENSIONS.update(s)

def detect_category_by_extension(ext: str):
    ext = ext.lower().lstrip(".")
    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            return cat
    # fallback to mimetype inspection
    mtype, _ = mimetypes.guess_type("file." + ext)
    if mtype:
        if mtype.startswith("image"): return "Images"
        if mtype.startswith("video"): return "Videos"
        if mtype.startswith("audio"): return "Audio"
        if mtype == "application/zip": return "Archives"
    return "Others"

def organize_directory(src: Path, dry_run: bool = False):
    """
    Scan src directory (non-recursive for top-level files), create category folders,
    move files into them. Returns a report dict.
    """
    if not src.exists() or not src.is_dir():
        raise ValueError("src must be an existing directory")

    report = {"moved": [], "skipped": [], "errors": []}
    # Optionally walk recursively; here we do only top-level files and optionally move from subfolders if desired.
    for item in src.iterdir():
        try:
            if item.is_dir():
                # skip category dirs to avoid infinite loop
                if item.name in CATEGORY_MAP.keys() or item.name in {"Others"}:
                    continue
                # we will not move directories by default
                report["skipped"].append(str(item))
                continue
            if item.is_file():
                ext = item.suffix.lstrip(".")
                category = detect_category_by_extension(ext)
                target_dir = src / category
                target_dir_exists = target_dir.exists()
                if not dry_run:
                    target_dir.mkdir(exist_ok=True)
                    dest = target_dir / item.name
                    # if destination exists, append suffix
                    if dest.exists():
                        base = dest.stem
                        suffix = dest.suffix
                        i = 1
                        while (target_dir / f"{base}_{i}{suffix}").exists():
                            i += 1
                        dest = target_dir / f"{base}_{i}{suffix}"
                    shutil.move(str(item), str(dest))
                    report["moved"].append({"from": str(item.name), "to": str(dest.relative_to(src))})
                else:
                    report["moved"].append({"from": str(item.name), "to": str((target_dir / item.name).relative_to(src))})
        except Exception as e:
            report["errors"].append({"item": str(item), "error": str(e)})
    return report
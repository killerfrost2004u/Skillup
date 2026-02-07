import os
import shutil
import re

# Configuration
CSS_DIR = 'css'
JS_DIR = 'js'
SKIP_DIRS = {'node_modules', '.git', '.idea', '__pycache__'}
SCRIPT_NAME = os.path.basename(__file__)


def main():
    print("🧹 Starting Project Cleanup...")

    # 1. Create Directories if they don't exist
    if not os.path.exists(CSS_DIR):
        os.makedirs(CSS_DIR)
        print(f"📁 Created {CSS_DIR}/ folder")

    if not os.path.exists(JS_DIR):
        os.makedirs(JS_DIR)
        print(f"📁 Created {JS_DIR}/ folder")

    # 2. Identify and Move Files
    all_files = [f for f in os.listdir('.') if os.path.isfile(f)]

    moved_css = {}  # Maps old_filename -> new_relative_path
    moved_js = {}  # Maps old_filename -> new_relative_path

    for filename in all_files:
        if filename == SCRIPT_NAME:
            continue  # Don't move this script itself

        # Move CSS
        if filename.lower().endswith('.css'):
            new_path = os.path.join(CSS_DIR, filename)
            shutil.move(filename, new_path)
            moved_css[filename] = f"{CSS_DIR}/{filename}"
            print(f" -> Moved {filename} to {CSS_DIR}/")

        # Move JS
        elif filename.lower().endswith('.js'):
            new_path = os.path.join(JS_DIR, filename)
            shutil.move(filename, new_path)
            moved_js[filename] = f"{JS_DIR}/{filename}"
            print(f" -> Moved {filename} to {JS_DIR}/")

    # 3. Update HTML References
    html_files = [f for f in os.listdir('.') if f.lower().endswith('.html')]

    print(f"\n📝 Updating {len(html_files)} HTML files...")

    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace JS references (src="file.js")
        for old_name, new_path in moved_js.items():
            # Regex to match src="old_name" or src='./old_name'
            # We use re.escape to handle filenames with dots or dashes safely
            pattern = r'(src=["\'])(?:\./)?' + re.escape(old_name) + r'(["\'])'
            content = re.sub(pattern, r'\1' + new_path + r'\2', content)

        # Replace CSS references (href="file.css")
        for old_name, new_path in moved_css.items():
            pattern = r'(href=["\'])(?:\./)?' + re.escape(old_name) + r'(["\'])'
            content = re.sub(pattern, r'\1' + new_path + r'\2', content)

        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated links in {html_file}")

    # 4. Fix CSS Image Paths (Background images need ../ now)
    print("\n🎨 Fixing CSS background image paths...")

    for css_file in os.listdir(CSS_DIR):
        file_path = os.path.join(CSS_DIR, css_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Function to prepend ../ to urls that are not absolute or data URIs
        def fix_css_url(match):
            quote = match.group(1) or ""
            url = match.group(2).strip()

            # Skip if it's a web link, data URI, or already goes up a directory
            if url.startswith(('http', 'https', 'data:', '..', '/')):
                return match.group(0)

            return f"url({quote}../{url}{quote})"

        # Regex looks for url("...") or url('...') or url(...)
        new_content = re.sub(r'url\s*\(\s*(["\']?)([^"\'\)]+)\1\s*\)', fix_css_url, content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ Fixed image paths in {css_file}")

    print("\n✨ Clean up complete! You can delete this script now.")


if __name__ == "__main__":
    main()
import os
import shutil
import re

# Configuration
CSS_DIR = 'css'
JS_DIR = 'js'


def main():
    print("Rewinding project structure... ↺")

    # 1. Move CSS files back to root
    if os.path.exists(CSS_DIR):
        for filename in os.listdir(CSS_DIR):
            if filename.lower().endswith('.css'):
                src = os.path.join(CSS_DIR, filename)
                dst = filename
                try:
                    shutil.move(src, dst)
                    print(f" <- Moved {filename} back to root")
                except Exception as e:
                    print(f"Error moving {filename}: {e}")

    # 2. Move JS files back to root
    if os.path.exists(JS_DIR):
        for filename in os.listdir(JS_DIR):
            if filename.lower().endswith('.js'):
                src = os.path.join(JS_DIR, filename)
                dst = filename
                try:
                    shutil.move(src, dst)
                    print(f" <- Moved {filename} back to root")
                except Exception as e:
                    print(f"Error moving {filename}: {e}")

    # 3. Revert HTML Links (Remove 'css/' and 'js/' prefixes)
    html_files = [f for f in os.listdir('.') if f.lower().endswith('.html')]
    print(f"\n📝 Reverting links in {len(html_files)} HTML files...")

    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Regex to remove js/ prefix from src="js/..." or src='js/...'
        # Matches src="js/ or src='js/ (and optional ./ before it)
        content = re.sub(r'(src=["\'])(?:\./)?js/', r'\1', content)

        # Regex to remove css/ prefix from href="css/..." or href='css/...'
        content = re.sub(r'(href=["\'])(?:\./)?css/', r'\1', content)

        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed links in {html_file}")

    # 4. Revert CSS Image Paths (Remove '../')
    # Note: Files are now back in the root, so we process them there.
    css_files = [f for f in os.listdir('.') if f.lower().endswith('.css')]
    print(f"\n🎨 Reverting image paths in {len(css_files)} CSS files...")

    for css_file in css_files:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Regex to find url('../image.png') and change to url('image.png')
        # Captures url(" or url(' or url(
        # Matches ../
        content = re.sub(r'(url\s*\(\s*["\']?)\.\./', r'\1', content)

        if content != original_content:
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed paths in {css_file}")

    # 5. Clean up empty folders
    if os.path.exists(CSS_DIR) and not os.listdir(CSS_DIR):
        os.rmdir(CSS_DIR)
        print("\n🗑️  Deleted empty 'css' folder")

    if os.path.exists(JS_DIR) and not os.listdir(JS_DIR):
        os.rmdir(JS_DIR)
        print("🗑️  Deleted empty 'js' folder")

    print("\n✨ Undo complete! Project is back to original state.")


if __name__ == "__main__":
    main()
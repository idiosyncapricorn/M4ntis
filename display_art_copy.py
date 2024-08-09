Y = '\033[33m'  # Green
W = '\033[0m'   # Reset
C = '\033[36m'  # Cyan
def display_ascii_art(file_path):
    try:
        with open(file_path, 'r') as file:
            ascii_art = file.read()
            print(f"{C}{ascii_art}{W}")
    except FileNotFoundError:
        print("Error: ASCII art file not found.")

def display_banner_art(file_path):
    try:
        with open(file_path, 'r') as file:
            banner_art = file.read()
            print(f"{W}{banner_art}{W}")
    except FileNotFoundError:
            print("Error: ASCII art file not found.")

if __name__ == "__main__":
    display_ascii_art('/Users/gavinmorrison/Desktop/Audify/audify/ascii_art.txt')
   
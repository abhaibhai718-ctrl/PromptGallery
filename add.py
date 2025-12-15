import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os
import datetime

# --- SETUP PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- CORE LOGIC ---
def compress_and_save(source_path):
    try:
        # Clean path string
        source_path = source_path.replace("{", "").replace("}", "")
        
        img = Image.open(source_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Resize logic
        max_width = 1080
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Create filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"img_{timestamp}.jpg"
        save_path = os.path.join(IMG_DIR, filename)
        
        # Save
        img.save(save_path, "JPEG", quality=70)
        return filename
    except Exception as e:
        messagebox.showerror("Error", f"Image process failed: {str(e)}")
        return None

def update_html(filename, prompt):
    clean_prompt = prompt.replace('"', '&quot;').replace("'", "&#39;")
    new_card = f"""
    <div class="card" onclick="copyPrompt(this, '{clean_prompt}')">
        <img src="images/{filename}" alt="Prompt Image" loading="lazy">
        <div class="overlay">Tap to Copy</div>
    </div>
    """
    
    if not os.path.exists(HTML_FILE):
        create_base_html()
        
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    marker = '<div class="gallery-grid">'
    if marker in content:
        new_content = content.replace(marker, marker + "\n" + new_card)
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

def create_base_html():
    base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Prompt Library</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: sans-serif; margin: 0; padding: 10px; }
        h1 { text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 20px;}
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
        }
        .card {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            aspect-ratio: 1 / 1;
            cursor: pointer;
            background: #222;
            transition: transform 0.1s;
        }
        .card:active { transform: scale(0.98); }
        .card img { width: 100%; height: 100%; object-fit: cover; }
        .overlay {
            position: absolute; bottom: 0; left: 0; right: 0;
            background: rgba(0,0,0,0.8); color: white;
            font-size: 12px; text-align: center; padding: 8px;
            opacity: 0; transition: opacity 0.2s;
        }
        .card:hover .overlay { opacity: 1; }
        @media (hover: none) { .overlay { opacity: 1; background: rgba(0,0,0,0.5); } }
        
        /* Toast */
        #toast {
            visibility: hidden; min-width: 200px; background-color: #4CAF50;
            color: white; text-align: center; border-radius: 4px; padding: 12px;
            position: fixed; z-index: 1; bottom: 30px; left: 50%;
            transform: translateX(-50%); font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        #toast.show { visibility: visible; animation: fadein 0.3s, fadeout 0.3s 2.0s; }
        @keyframes fadein { from {bottom: 0; opacity: 0;} to {bottom: 30px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 30px; opacity: 1;} to {bottom: 0; opacity: 0;} }
    </style>
</head>
<body>
    <h1>My Prompts</h1>
    <div class="gallery-grid"></div>
    <div id="toast">Copied!</div>
    <script>
        function copyPrompt(card, text) {
            navigator.clipboard.writeText(text).then(function() {
                var x = document.getElementById("toast");
                x.className = "show";
                setTimeout(function(){ x.className = x.className.replace("show", ""); }, 2300);
            });
        }
    </script>
</body>
</html>"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(base_html)

# --- DRAG AND DROP HANDLER ---
def handle_drop(event):
    path = event.data
    process_entry(path)

def manual_select():
    path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.png;*.jpeg;*.webp")])
    if path:
        process_entry(path)

def process_entry(image_path):
    prompt_text = text_prompt.get("1.0", tk.END).strip()
    if not prompt_text:
        messagebox.showwarning("Ruko!", "Pehle prompt to likho bhai!")
        return
    
    # Process
    saved_filename = compress_and_save(image_path)
    if saved_filename:
        update_html(saved_filename, prompt_text)
        
        # UI Feedback
        lbl_status.config(text=f"✅ Saved!", fg="#4CAF50")
        text_prompt.delete("1.0", tk.END)
        root.after(2000, lambda: lbl_status.config(text="Drag Image Here", fg="#aaa"))

# --- GUI SETUP ---
root = TkinterDnD.Tk()
root.title("Visual Prompt Library")
root.geometry("400x350")
root.configure(bg="#f0f0f0")

# Prompt Area
tk.Label(root, text="Paste Prompt:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(15,5))
text_prompt = tk.Text(root, height=6, width=40, borderwidth=2, relief="flat", font=("Consolas", 10))
text_prompt.pack(padx=20)

# Drop Zone (FIXED LINE: Changed 'dashed' to 'groove')
drop_frame = tk.Frame(root, bg="#e0e0e0", width=360, height=120, relief="groove", borderwidth=2)
drop_frame.pack(pady=20, fill=tk.BOTH, expand=True, padx=20)
drop_frame.pack_propagate(False)

lbl_status = tk.Label(drop_frame, text="Drag Image Here\n(or click to select)", bg="#e0e0e0", fg="#aaa", font=("Arial", 12))
lbl_status.place(relx=0.5, rely=0.5, anchor="center")

# Bindings
drop_frame.drop_target_register(DND_FILES)
drop_frame.dnd_bind('<<Drop>>', handle_drop)
drop_frame.bind("<Button-1>", lambda e: manual_select()) # Click to select

# Init
if not os.path.exists(HTML_FILE):
    create_base_html()

root.mainloop()
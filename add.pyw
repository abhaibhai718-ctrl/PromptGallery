import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
import os
import datetime
import html
import subprocess # Ye naya hai (Automation ke liye)

# --- SETUP PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- CORE LOGIC ---
def compress_and_save(source_path):
    try:
        source_path = source_path.replace("{", "").replace("}", "")
        img = Image.open(source_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        max_width = 1080
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"img_{timestamp}.jpg"
        save_path = os.path.join(IMG_DIR, filename)
        
        img.save(save_path, "JPEG", quality=75)
        return filename
    except Exception as e:
        messagebox.showerror("Error", f"Image process failed: {str(e)}")
        return None

def update_html(filename, prompt):
    clean_prompt = html.escape(prompt)
    new_card = f"""
    <div class="card" data-prompt="{clean_prompt}" onclick="copyPrompt(this)">
        <img src="images/{filename}" alt="Prompt" loading="lazy">
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Visual Prompt Library</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 10px; -webkit-tap-highlight-color: transparent; }
        h1 { text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 20px; font-weight: normal; }
        .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 8px; padding-bottom: 50px; }
        .card { position: relative; border-radius: 12px; overflow: hidden; aspect-ratio: 1 / 1; cursor: pointer; background: #222; transition: transform 0.1s; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .card:active { transform: scale(0.96); }
        .card img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .overlay { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); color: white; font-size: 13px; text-align: center; padding: 15px 5px 8px 5px; opacity: 0; transition: opacity 0.2s; }
        .card:hover .overlay { opacity: 1; }
        #toast { visibility: hidden; min-width: 200px; background-color: #333; color: #fff; text-align: center; border-radius: 50px; padding: 12px 20px; position: fixed; z-index: 100; bottom: 40px; left: 50%; transform: translateX(-50%); font-size: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid #444; }
        #toast.show { visibility: visible; animation: fadein 0.3s, fadeout 0.3s 2.0s; }
        @keyframes fadein { from {bottom: 20px; opacity: 0;} to {bottom: 40px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 40px; opacity: 1;} to {bottom: 20px; opacity: 0;} }
    </style>
</head>
<body>
    <h1>My Prompts</h1>
    <div class="gallery-grid"></div>
    <div id="toast">Copied to clipboard!</div>
    <script>
        async function copyPrompt(card) {
            const text = card.getAttribute('data-prompt');
            try { await navigator.clipboard.writeText(text); showToast("Copied!"); } 
            catch (err) {
                const textarea = document.createElement('textarea'); textarea.value = text;
                document.body.appendChild(textarea); textarea.select();
                try { document.execCommand('copy'); showToast("Copied!"); } catch (e) { showToast("Error"); }
                document.body.removeChild(textarea);
            }
        }
        function showToast(msg) { var x = document.getElementById("toast"); x.innerText = msg; x.className = "show"; setTimeout(function(){ x.className = x.className.replace("show", ""); }, 2000); }
    </script>
</body>
</html>"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(base_html)

# --- AUTOMATION MAGIC ---
def auto_sync():
    try:
        # 1. Update UI Status
        lbl_status.config(text="☁ Uploading to Web...", fg="#2196F3")
        root.update() # Force UI refresh
        
        # 2. Run Git Commands
        # git add .
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # git commit -m "Auto update"
        subprocess.run(["git", "commit", "-m", "Auto update via Tool"], cwd=BASE_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # git push
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # 3. Success
        lbl_status.config(text="✅ Live on Web!", fg="#4CAF50")
        
        # Reset after 3 seconds
        root.after(3000, lambda: lbl_status.config(text="Drag Image Here", fg="#aaa"))
        
    except FileNotFoundError:
        lbl_status.config(text="❌ Git not found!", fg="red")
        messagebox.showerror("Error", "Git install nahi hai!\nGoogle 'Git for Windows' and install it.")
    except Exception as e:
        lbl_status.config(text="❌ Upload Failed", fg="red")
        print(e) # Print error to console for debugging
        # Don't show popup for every error to keep flow fast, just status label

# --- MAIN HANDLER ---
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
        messagebox.showwarning("Wait", "Prompt text missing!")
        return
    
    saved_filename = compress_and_save(image_path)
    if saved_filename:
        update_html(saved_filename, prompt_text)
        text_prompt.delete("1.0", tk.END)
        
        # Call Automation
        auto_sync()

# --- GUI SETUP ---
root = TkinterDnD.Tk()
root.title("Visual Prompt Library")
root.geometry("400x350")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Paste Prompt:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(15,5))
text_prompt = tk.Text(root, height=6, width=40, borderwidth=2, relief="flat", font=("Consolas", 10))
text_prompt.pack(padx=20)

drop_frame = tk.Frame(root, bg="#e0e0e0", width=360, height=120, relief="groove", borderwidth=2)
drop_frame.pack(pady=20, fill=tk.BOTH, expand=True, padx=20)
drop_frame.pack_propagate(False)

lbl_status = tk.Label(drop_frame, text="Drag Image Here\n(or click to select)", bg="#e0e0e0", fg="#aaa", font=("Arial", 12))
lbl_status.place(relx=0.5, rely=0.5, anchor="center")

drop_frame.drop_target_register(DND_FILES)
drop_frame.dnd_bind('<<Drop>>', handle_drop)
drop_frame.bind("<Button-1>", lambda e: manual_select())

if not os.path.exists(HTML_FILE):
    create_base_html()

root.mainloop()
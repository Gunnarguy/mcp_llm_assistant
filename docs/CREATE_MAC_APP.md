# Creating a Mac App for MCP Assistant

## 🎯 Quick Option: Terminal Launcher (Ready Now!)

**Double-click this file to start the app:**
```
MCP_Assistant_Launcher.sh
```

Just double-click it in Finder! It will:
1. ✅ Open a Terminal window
2. ✅ Start both backend and frontend
3. ✅ Open your browser to the app
4. ✅ Show you status updates

**To stop:** Just close the Terminal window or press Cmd+W

---

## 🍎 Native Mac App Option: Using Automator

Follow these steps to create a **real macOS .app** that shows up like any other Mac app:

### Step 1: Open Automator

1. Open **Spotlight** (Cmd+Space)
2. Type "Automator" and press Enter
3. Click **"New Document"**
4. Choose **"Application"**

### Step 2: Configure the App

1. In the left sidebar, find **"Run Shell Script"** under "Utilities"
2. **Drag** "Run Shell Script" into the workflow area on the right
3. At the top, change **"Pass input"** dropdown to **"as arguments"**
4. In the text box, paste this script:

```bash
#!/bin/bash

# Get the directory where app is located
APP_DIR="/Users/gunnarhostetler/Documents/GitHub/MCP_Home/mcp_llm_assistant"
cd "$APP_DIR"

# Open Terminal and run the launcher
osascript -e 'tell app "Terminal"
    do script "cd '"$APP_DIR"' && ./MCP_Assistant_Launcher.sh"
    activate
end tell'
```

### Step 3: Save the App

1. Press **Cmd+S** to save
2. Save it as: **"MCP Assistant"**
3. Save location: Choose **Desktop** or **Applications** folder
4. Click **Save**

### Step 4: Set a Custom Icon (Optional)

1. Find a nice icon (I can help generate one if you want)
2. Right-click the MCP Assistant.app
3. Click "Get Info"
4. Drag your icon image onto the small icon in the top-left of the Info window

### ✅ Done!

Now you can:
- Double-click **MCP Assistant.app** from wherever you saved it
- Add it to your Dock by dragging it there
- Launch it like any other Mac app

---

## 🚀 Advanced Option: PyInstaller (For Distribution)

If you want to **share the app with others** who don't have Python installed:

### 1. Install PyInstaller

```bash
cd /Users/gunnarhostetler/Documents/GitHub/MCP_Home/mcp_llm_assistant
source venv/bin/activate
pip install pyinstaller
```

### 2. Create the launcher Python script

I'll create this in the next step if you want to go this route.

### 3. Build the app

```bash
pyinstaller --onefile --windowed --name "MCP Assistant" launcher.py
```

This creates a standalone app in the `dist/` folder that you can share.

---

## 📝 Which Option Should You Choose?

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Shell Script** | ✅ Ready now<br>✅ Easy to modify | ❌ Shows Terminal | Personal use |
| **Automator App** | ✅ Native Mac app<br>✅ Easy to create<br>✅ Can customize icon | ❌ Still opens Terminal<br>❌ Harder to distribute | Personal use, looks professional |
| **PyInstaller** | ✅ Fully standalone<br>✅ Can share with others<br>✅ No Terminal window | ❌ Takes time to build<br>❌ Larger file size | Distribution to others |

---

## 🎨 Want a Custom Icon?

I can help you:
1. Generate a nice icon using AI
2. Download an icon from the web
3. Use the default Python/Terminal icon

Let me know if you want to add a custom icon!

---

## ⚡ Quick Start Right Now

**Just do this:**

1. Open Finder
2. Navigate to: `/Users/gunnarhostetler/Documents/GitHub/MCP_Home/mcp_llm_assistant`
3. Double-click **`MCP_Assistant_Launcher.sh`**

That's it! The app will start in a Terminal window.

---

## 🆘 Troubleshooting

**"Permission denied" error?**
```bash
chmod +x MCP_Assistant_Launcher.sh
```

**"Cannot open app from unidentified developer"?**
1. Right-click the .app
2. Select "Open"
3. Click "Open" in the dialog

**Want to change the script?**
- Edit `MCP_Assistant_Launcher.sh` with any text editor

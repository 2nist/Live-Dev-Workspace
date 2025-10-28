# Building the ArrangerControl Max for Live Device

This guide shows you how to build the device in Max step-by-step, with ASCII diagrams showing object placement and connections.

## Prerequisites

- Max for Live installed (comes with Ableton Live Suite)
- Max application (part of Max for Live install)

## Step-by-Step Build

### 1. Create a New Max for Live Audio Effect

1. Open Max (the application, not Live)
2. File → New → New Max for Live Audio Effect
3. This creates a basic template with audio in/out

### 2. Delete the Default Audio Chain

1. Delete the `plugin~` and `plugout~` objects (we don't need audio routing)
2. You should have a blank patcher

### 3. Add the Core OSC Objects

Add these objects by pressing `N` and typing the object name:

```
┌─────────────────────────────────────────────────────────────┐
│  Patcher Window                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [udpsend 127.0.0.1 12000]    [udpreceive 12001]           │
│         (obj-1)                      (obj-2)                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**To create:**
- Press `N` → type `udpsend 127.0.0.1 12000` → Enter
- Press `N` → type `udpreceive 12001` → Enter

### 4. Add Play/Stop Controls

Create buttons and message boxes for transport:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│     [button]          [button]                              │
│     (Play)            (Stop)                                │
│        │                 │                                  │
│        ▼                 ▼                                  │
│  [/live/play]      [/live/stop]                             │
│        │                 │                                  │
│        └─────────┬───────┘                                  │
│                  ▼                                          │
│         [udpsend 127.0.0.1 12000]                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**To create:**
- Press `N` → type `button` → Enter (make 2 of these)
- Press `N` → type `message /live/play` → Enter
- Press `N` → type `message /live/stop` → Enter
- Connect button outlets to message inlets (click outlet, drag to inlet)
- Connect both message outlets to `udpsend` inlet

### 5. Add Tempo Control

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              [number]                                       │
│              (Tempo)                                        │
│                 │                                           │
│                 ▼                                           │
│        [/live/set_tempo $1]                                 │
│                 │                                           │
│                 ▼                                           │
│         [udpsend 127.0.0.1 12000]                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**To create:**
- Press `N` → type `number` → Enter
- Press `N` → type `message /live/set_tempo $1` → Enter
- Connect number outlet to message inlet
- Connect message outlet to `udpsend` inlet

**Note:** The `$1` in the message will be replaced by the number value.

### 6. Add Scene Creation

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              [button]                                       │
│            (New Scene)                                      │
│                 │                                           │
│                 ▼                                           │
│      [/live/create_scene_index -1]                          │
│                 │                                           │
│                 ▼                                           │
│         [udpsend 127.0.0.1 12000]                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**To create:**
- Press `N` → type `button` → Enter
- Press `N` → type `message /live/create_scene_index -1` → Enter
- Connect button outlet to message inlet
- Connect message outlet to `udpsend` inlet

### 7. Add Reply Display

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│         [udpreceive 12001]                                  │
│                 │                                           │
│                 ▼                                           │
│         [message set $1]                                    │
│         (displays reply)                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**To create:**
- Use the `udpreceive 12001` object from step 3
- Press `N` → type `message` → Enter (this creates an empty message box)
- Connect `udpreceive` outlet to message inlet (right inlet, not left!)

### 8. Add Labels (Comments)

Press `C` to create comment boxes and type labels:
- "Play" above the play button
- "Stop" above the stop button
- "Tempo" above the tempo number
- "New Scene" above the scene button
- "Server Reply:" above the reply message

### 9. Complete Wiring Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│  Max Patcher - ArrangerControl                                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  OSC SEND                                      OSC RECEIVE           │
│  ┌─────────────────────────┐                  ┌────────────┐        │
│  │ udpsend 127.0.0.1 12000 │                  │ udpreceive │        │
│  └───────▲─────────────────┘                  │   12001    │        │
│          │                                    └──────┬─────┘        │
│          │                                           │              │
│  ┌───────┴──────────┬──────────┬──────────┐         │              │
│  │                  │          │          │         │              │
│  │                  │          │          │         │              │
│ [Play]           [Stop]    [Tempo]   [New Scene]    │              │
│  btn              btn       number      btn         │              │
│  │                │          │          │           │              │
│  ▼                ▼          ▼          ▼           ▼              │
│ [/live/play]  [/live/stop] [tempo $1] [scene -1]  [msg]           │
│  msg              msg         msg        msg      (reply)          │
│                                                                      │
│  PRESENTATION MODE (what user sees):                                │
│  ┌────────────────────────────────────────────────────┐             │
│  │  [Play] [Stop]  [120▼] [New Scene]                │             │
│  │                                                    │             │
│  │  Server Reply: {"status": "playing"}              │             │
│  └────────────────────────────────────────────────────┘             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 10. Set Up Presentation Mode

Presentation mode is what the user sees in Live.

1. **Enable presentation mode:**
   - View → Presentation Mode (or click the presentation toggle)

2. **Add objects to presentation:**
   - Right-click each button/number/message → "Add to Presentation"
   - Select all UI objects (buttons, number, reply message)
   - Object → Add to Presentation

3. **Arrange in presentation:**
   - In presentation view, drag objects to arrange them nicely
   - Resize buttons for easier clicking (click and drag corners)
   - Suggested layout:
     ```
     [  Play  ] [  Stop  ] [ 120 ▼] [ New Scene ]
     
     Server Reply:
     ┌─────────────────────────────────────────┐
     │ {"status": "ok"}                        │
     └─────────────────────────────────────────┘
     ```

### 11. Lock and Save

1. **Lock the patcher:**
   - Click the lock icon (top left)
   - This prevents accidental editing in Live

2. **Save as .amxd:**
   - File → Save As...
   - Name: `ArrangerControl.amxd`
   - Location: `ableton-live-testing/devices/`
   - **Important:** Choose "Max for Live Device (.amxd)" as the file type

### 12. Test in Live

1. **Open Ableton Live**
2. **Drag the device onto a MIDI track:**
   - Navigate to the saved .amxd file
   - Drag onto any track
3. **Start the OSC server** (in terminal):
   ```bash
   export PYTHONPATH="$PWD/python/src"
   ./.venv/bin/python python/src/arranger/live_bridge/osc_server.py --use-live
   ```
4. **Click buttons in the device**
   - Click Play → should see OSC server log "playing"
   - Click Stop → should see "stopped"
   - Change tempo → should see tempo change message
   - Click New Scene → should create scene in Live

## Troubleshooting

**Device doesn't appear in Live:**
- Make sure you saved as `.amxd` format
- Try placing in: `~/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect/`
- Rescan Live's browser (right-click → Rescan)

**Buttons don't work:**
- Make sure OSC server is running first
- Check Max window (in Live) for errors: View → Show Max Window
- Verify message boxes have correct OSC paths (`/live/play`, etc.)

**No replies shown:**
- Check `udpreceive 12001` is connected to the message box
- Make sure connection goes to the **right inlet** of the message box
- OSC server sends replies to port 12001

**Max window shows "connect failed":**
- OSC server not running or wrong port
- Check server is on 127.0.0.1:12000

## Quick Reference: Object Types

| Object Name | What It Does | How to Create |
|-------------|--------------|---------------|
| `button` | Bang/trigger | Press N, type "button" |
| `message <text>` | Sends text/OSC | Press N, type "message /live/play" |
| `number` | Number input | Press N, type "number" |
| `udpsend <ip> <port>` | Send OSC | Press N, type "udpsend 127.0.0.1 12000" |
| `udpreceive <port>` | Receive OSC | Press N, type "udpreceive 12001" |
| `comment <text>` | Label | Press C, type text |

## Connection Tips

- **Click and drag** from outlet (bottom of object) to inlet (top of object)
- **Hover** to see connection hints
- **Hold Option** while connecting to create a segmented patch cord
- **Double-click** a patch cord to delete it

## Advanced: Adding More Controls

Want to add more? Here are common additions:

**Get Current Tempo:**
```
[button "Get Tempo"]
    │
    ▼
[/live/get_tempo]
    │
    ▼
[udpsend 127.0.0.1 12000]
```

**Trigger Scene by Index:**
```
[number "Scene Index"]
    │
    ▼
[/live/trigger_scene $1]
    │
    ▼
[udpsend 127.0.0.1 12000]
```

**Create Clip:**
```
[number "Track"] [number "Scene"] [number "Length"]
     │               │                │
     └───────┬───────┴────────────────┘
             ▼
    [pak 0 0 4.]
             │
             ▼
    [prepend /live/clip/create]
             │
             ▼
    [udpsend 127.0.0.1 12000]
```

## Done!

You now have a working Max for Live device that controls the arranger system. You can extend it with more buttons, sliders, and controls as needed.

For the web dashboard alternative (no Max required), see the main `README.md` in this folder.

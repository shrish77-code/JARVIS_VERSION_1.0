# J.A.R.V.I.S. Web Interface

A modern, cinematic web interface for your J.A.R.V.I.S. AI Assistant with stunning hologram effects and real-time status updates.

## Features

- **Futuristic Hologram Visualization**: 3D animated hologram with particle effects using Three.js
- **Real-time Status Updates**: Live assistant status, microphone state, and chat updates
- **Modern UI Design**: Cinematic dark theme with glowing effects and animations
- **Voice Control**: Click-to-speak with visual feedback
- **Communication Log**: Real-time chat interface showing all conversations
- **System Monitoring**: Neural interface display and system logs
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. Install all required dependencies:
```bash
pip install -r Requirements.txt
```

2. Make sure your `.env` file is configured with all necessary API keys:
   - `CohereAPIKey`
   - `GeminiAPIKey`
   - `GroqAPIKey`
   - `Username`
   - `Assistantname`
   - `InputLanguage`
   - `AssistantVoice`

## Running the Web Interface

### Option 1: Web Interface Only
Run the web server and backend together:
```bash
python StartWeb.py
```

Then open your browser to: **http://localhost:5000**

### Option 2: Original Tkinter GUI
To use the original Tkinter interface:
```bash
python Main.py
```

## How to Use

1. **Start the Interface**: Run `python StartWeb.py`
2. **Open Browser**: Navigate to http://localhost:5000
3. **Voice Interaction**: Click the microphone button to speak
4. **View Status**: Watch the hologram change based on assistant state:
   - **Idle**: Slow, calm animation (Available)
   - **Listening**: Fast pulsing cyan hologram
   - **Thinking/Processing**: Rapid rotation with blue tones
   - **Answering**: Bright, energetic animation
5. **Check Chat**: All conversations appear in the Communication Log

## Architecture

### Frontend (Web Interface)
- **HTML**: `/Frontend/web/index.html`
- **CSS**: `/Frontend/web/static/style.css`
- **JavaScript**: `/Frontend/web/static/app.js`

### Backend (Flask Server)
- **WebServer.py**: Flask server providing API endpoints
- **Main.py**: Core backend logic and AI processing
- **Frontend/GUI.py**: Updated to write status to files

### API Endpoints
- `GET /api/state`: Returns current assistant status, mic state, chat, and database
- `POST /api/toggle_mic`: Toggles microphone on/off

### Data Flow
1. User clicks mic button → POST to `/api/toggle_mic`
2. Backend updates `Mic.data` file
3. Main.py processes voice input
4. Backend updates status files (`Status.data`, `Responses.data`, `Database.data`)
5. Frontend polls `/api/state` every 700ms
6. UI updates automatically with new data

## File Structure

```
project/
├── StartWeb.py                 # Web interface launcher
├── WebServer.py                # Flask API server
├── Main.py                     # Backend logic
├── Frontend/
│   ├── GUI.py                  # Tkinter GUI (optional)
│   ├── web/
│   │   ├── index.html          # Main HTML
│   │   └── static/
│   │       ├── style.css       # Styling
│   │       └── app.js          # JavaScript
│   └── Files/
│       ├── Mic.data            # Microphone state
│       ├── Status.data         # Assistant status
│       ├── Responses.data      # Chat responses
│       └── Database.data       # Chat history
└── Backend/
    ├── Model.py                # Decision making
    ├── Chatbot.py              # Conversation AI
    ├── SpeechToText.py         # Voice recognition
    ├── TextToSpeech.py         # Voice synthesis
    ├── Automation.py           # Task automation
    └── RealtimeSearchEngine.py # Web search
```

## Customization

### Change Colors
Edit `/Frontend/web/static/style.css`:
```css
:root {
    --primary: #00d9ff;      /* Main color */
    --secondary: #0099ff;    /* Secondary color */
    --accent: #00ffcc;       /* Accent color */
}
```

### Adjust Hologram Effects
Edit `/Frontend/web/static/app.js`:
- Particle count: Line 212 (`particleCount`)
- Animation speed: Lines 291-292, 311-312
- Ring count: Line 251 (`for(let i=0; i<4; i++)`)

### Change Status Colors
The hologram automatically changes color based on state:
- Idle: Cyan (#00ffcc)
- Listening: Bright cyan (#00ffcc)
- Thinking: Blue (#0099ff)
- Answering: Light cyan (#00d9ff)

## Troubleshooting

### Web server won't start
- Check if port 5000 is already in use
- Make sure Flask is installed: `pip install flask`

### Hologram not showing
- Ensure Three.js is loading (check browser console)
- Try a different browser (Chrome/Firefox recommended)

### Microphone not working
- Check Chrome's speech recognition permissions
- Ensure `Data/Voice.html` exists
- Verify Chrome/Edge browser is installed at default location

### Status not updating
- Check that backend is running (StartWeb.py)
- Verify `/Frontend/Files/` directory exists
- Check browser console for errors

## Browser Compatibility

Recommended browsers:
- Chrome (latest)
- Edge (latest)
- Firefox (latest)

**Note**: Speech recognition requires Chrome or Edge.

## Performance Tips

1. Lower particle count for slower systems (edit `app.js` line 212)
2. Increase polling interval (edit `app.js` line 54, change 700 to higher value)
3. Disable grid overlay (comment out in `index.html` line 13)
4. Reduce animation complexity (edit hologram update functions)

## Support

For issues or questions, check:
- Browser console for JavaScript errors
- Terminal output for backend errors
- Make sure all dependencies are installed
- Verify API keys in `.env` file

Enjoy your futuristic J.A.R.V.I.S. interface!

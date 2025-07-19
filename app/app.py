from flask import Flask
import os
import random

app = Flask(__name__)

# Get the version from an environment variable, default to 1.0
# This allows us to change the version without changing the code
APP_VERSION = os.environ.get('APP_VERSION', '1.0')

# Space-themed messages that rotate
SPACE_MESSAGES = [
    "Initiating hyperspace jump sequence...",
    "Scanning for habitable exoplanets...",
    "Deploying quantum entanglement communicators...",
    "Calibrating warp drive containment field...",
    "Establishing contact with distant star systems...",
    "Running stellar cartography algorithms...",
    "Analyzing cosmic background radiation...",
    "Synchronizing with galactic positioning satellites..."
]

@app.route('/')
def hello():
    """
    Main route that returns a space-themed welcome message with the application version.
    """
    # Select a random space message
    space_message = random.choice(SPACE_MESSAGES)
    
    # HTML for space-themed styling
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 Starship CI/CD Command Center</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
            
            body {{
                font-family: 'Orbitron', 'Courier New', monospace;
                margin: 0;
                height: 100vh;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
                background-attachment: fixed;
                overflow: hidden;
                position: relative;
            }}
            
            /* Animated stars background */
            .stars {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }}
            
            .star {{
                position: absolute;
                background: white;
                border-radius: 50%;
                animation: twinkle 2s infinite alternate;
            }}
            
            .star.small {{
                width: 1px;
                height: 1px;
            }}
            
            .star.medium {{
                width: 2px;
                height: 2px;
            }}
            
            .star.large {{
                width: 3px;
                height: 3px;
            }}
            
            @keyframes twinkle {{
                0% {{ opacity: 0.3; }}
                100% {{ opacity: 1; }}
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-20px); }}
            }}
            
            @keyframes glow {{
                0%, 100% {{ box-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 15px #00ffff; }}
                50% {{ box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff; }}
            }}
            
            .command-center {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                position: relative;
                z-index: 10;
            }}
            
            .control-panel {{
                background: rgba(0, 20, 40, 0.9);
                border: 2px solid #00ffff;
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                backdrop-filter: blur(10px);
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
                animation: float 6s ease-in-out infinite;
                max-width: 600px;
                margin: 20px;
            }}
            
            .title {{
                color: #00ffff;
                font-size: 2.5em;
                font-weight: 900;
                margin: 0 0 10px 0;
                text-shadow: 0 0 10px #00ffff;
                letter-spacing: 2px;
            }}
            
            .subtitle {{
                color: #ffffff;
                font-size: 1.1em;
                margin: 0 0 20px 0;
                opacity: 0.8;
                font-weight: 400;
            }}
            
            .status-message {{
                color: #00ff88;
                font-size: 1.1em;
                margin: 20px 0;
                padding: 15px;
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid #00ff88;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
            }}
            
            .version-display {{
                display: inline-block;
                margin: 20px 0;
                padding: 12px 24px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                color: #ffffff;
                font-weight: 700;
                font-size: 1.2em;
                border-radius: 25px;
                border: none;
                animation: glow 2s ease-in-out infinite alternate;
                letter-spacing: 1px;
            }}
            
            .ship-icon {{
                font-size: 3em;
                margin: 20px 0;
                animation: float 4s ease-in-out infinite;
            }}
            
            .system-info {{
                color: #888;
                font-size: 0.9em;
                margin-top: 20px;
                font-family: 'Courier New', monospace;
            }}
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {{
                .title {{ font-size: 1.8em; }}
                .control-panel {{ padding: 20px; margin: 10px; }}
            }}
        </style>
    </head>
    <body>
        <!-- Animated stars background -->
        <div class="stars" id="stars"></div>
        
        <div class="command-center">
            <div class="control-panel">
                <div class="ship-icon">🚀</div>
                <h1 class="title">STARSHIP CI/CD</h1>
                <p class="subtitle">Command Center Online</p>
                
                <div class="status-message">
                    STATUS: {space_message}
                </div>
                
                <div class="version-display">
                    BUILD VERSION: {APP_VERSION}
                </div>
                
                <div class="system-info">
                    ⭐ Deployed via GitOps Hyperspace Network<br>
                    🛸 Powered by Kubernetes Quantum Computing<br>
                    🌌 Jenkins Autonomous Navigation System
                </div>
            </div>
        </div>
        
        <script>
            // Generate random stars
            function createStars() {{
                const starsContainer = document.getElementById('stars');
                const numStars = 150;
                
                for (let i = 0; i < numStars; i++) {{
                    const star = document.createElement('div');
                    star.className = 'star';
                    
                    // Random size
                    const sizes = ['small', 'medium', 'large'];
                    star.classList.add(sizes[Math.floor(Math.random() * sizes.length)]);
                    
                    // Random position
                    star.style.left = Math.random() * 100 + '%';
                    star.style.top = Math.random() * 100 + '%';
                    
                    // Random animation delay
                    star.style.animationDelay = Math.random() * 2 + 's';
                    
                    starsContainer.appendChild(star);
                }}
            }}
            
            // Create stars when page loads
            createStars();
            
            // Optional: Refresh the page every 30 seconds to get a new space message
            // setTimeout(() => {{ location.reload(); }}, 30000);
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # Run the app on port 8080, accessible from any network interface
    app.run(host='0.0.0.0', port=8080)
from flask import Flask
import os

app = Flask(__name__)

# Get the version from an environment variable, default to 1.0
# This allows us to change the version without changing the code
APP_VERSION = os.environ.get('APP_VERSION', '1.0')

@app.route('/')
def hello():
    """
    Main route that returns a welcome message with the application version.
    """
    # HTML for some basic styling
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CI/CD Project</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f2f5;
            }}
            .container {{
                text-align: center;
                padding: 40px;
                border-radius: 12px;
                background-color: #ffffff;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #333;
                font-size: 2.5em;
            }}
            p {{
                color: #555;
                font-size: 1.2em;
                margin-top: -10px;
            }}
            .version-badge {{
                display: inline-block;
                margin-top: 20px;
                padding: 8px 15px;
                border-radius: 25px;
                background-color: #007bff;
                color: #fff;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to the Demo App Chrissi!</h1>
            <p>This application is deployed via a CI/CD pipeline.</p>
            <div class="version-badge">Version: {APP_VERSION}</div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # Run the app on port 8080, accessible from any network interface
    app.run(host='0.0.0.0', port=8080)

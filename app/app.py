from flask import Flask, render_template, jsonify
from kubernetes import client, config, watch
import os
import random
import threading
import json
from datetime import datetime, timezone
import time

app = Flask(__name__)

# Get the version from an environment variable
APP_VERSION = os.environ.get('APP_VERSION', '1.0')

# Global variables to store cluster activity
cluster_events = []
deployment_status = {}
pod_status = {}

# Space-themed messages
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

def init_kubernetes():
    """Initialize Kubernetes client"""
    try:
        # Try to load in-cluster config first (when running in pod)
        config.load_incluster_config()
        print("Loaded in-cluster Kubernetes config")
    except config.ConfigException:
        try:
            # Fallback to local kubeconfig (for development)
            config.load_kube_config()
            print("Loaded local Kubernetes config")
        except config.ConfigException:
            print("Could not load Kubernetes config")
            return None
    
    return client.ApiClient()

def watch_cluster_events():
    """Watch for cluster events in a background thread"""
    global cluster_events
    
    try:
        v1 = client.CoreV1Api()
        w = watch.Watch()
        
        print("Starting to watch cluster events...")
        
        for event in w.stream(v1.list_event_for_all_namespaces, timeout_seconds=0):
            event_type = event['type']
            event_obj = event['object']
            
            # Filter for events in our namespace or related to our app
            if (event_obj.involved_object.namespace in ['devops', 'argo'] or 
                'cicd-portfolio' in event_obj.involved_object.name or
                'jenkins' in event_obj.message.lower()):
                
                cluster_event = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'type': event_type,
                    'reason': event_obj.reason,
                    'message': event_obj.message,
                    'object': f"{event_obj.involved_object.kind}/{event_obj.involved_object.name}",
                    'namespace': event_obj.involved_object.namespace or 'cluster'
                }
                
                cluster_events.append(cluster_event)
                
                # Keep only last 50 events
                if len(cluster_events) > 50:
                    cluster_events.pop(0)
                    
                print(f"Event: {cluster_event}")
                
    except Exception as e:
        print(f"Error watching events: {e}")

def get_deployment_status():
    """Get current deployment status"""
    global deployment_status
    
    try:
        apps_v1 = client.AppsV1Api()
        deployments = apps_v1.list_namespaced_deployment(namespace='devops')
        
        for deployment in deployments.items:
            if 'cicd-portfolio' in deployment.metadata.name:
                deployment_status = {
                    'name': deployment.metadata.name,
                    'replicas': deployment.spec.replicas,
                    'ready_replicas': deployment.status.ready_replicas or 0,
                    'updated_replicas': deployment.status.updated_replicas or 0,
                    'available_replicas': deployment.status.available_replicas or 0,
                    'image': deployment.spec.template.spec.containers[0].image,
                    'conditions': []
                }
                
                if deployment.status.conditions:
                    for condition in deployment.status.conditions:
                        deployment_status['conditions'].append({
                            'type': condition.type,
                            'status': condition.status,
                            'reason': condition.reason or '',
                            'message': condition.message or ''
                        })
                        
    except Exception as e:
        print(f"Error getting deployment status: {e}")

def get_pod_status():
    """Get current pod status"""
    global pod_status
    
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace='devops')
        
        pod_status = {
            'pods': [],
            'total': 0,
            'running': 0,
            'pending': 0,
            'failed': 0
        }
        
        for pod in pods.items:
            if 'cicd-portfolio' in pod.metadata.name:
                pod_info = {
                    'name': pod.metadata.name,
                    'phase': pod.status.phase,
                    'ready': False,
                    'restarts': 0,
                    'age': '',
                    'node': pod.spec.node_name or 'Unknown'
                }
                
                # Check if pod is ready
                if pod.status.conditions:
                    for condition in pod.status.conditions:
                        if condition.type == 'Ready':
                            pod_info['ready'] = condition.status == 'True'
                
                # Count restarts
                if pod.status.container_statuses:
                    pod_info['restarts'] = sum(cs.restart_count for cs in pod.status.container_statuses)
                
                # Calculate age
                if pod.metadata.creation_timestamp:
                    age = datetime.now(timezone.utc) - pod.metadata.creation_timestamp
                    pod_info['age'] = f"{age.days}d {age.seconds//3600}h"
                
                pod_status['pods'].append(pod_info)
                pod_status['total'] += 1
                
                if pod.status.phase == 'Running':
                    pod_status['running'] += 1
                elif pod.status.phase == 'Pending':
                    pod_status['pending'] += 1
                elif pod.status.phase == 'Failed':
                    pod_status['failed'] += 1
                    
    except Exception as e:
        print(f"Error getting pod status: {e}")

def update_cluster_status():
    """Update cluster status periodically"""
    while True:
        get_deployment_status()
        get_pod_status()
        time.sleep(5)  # Update every 5 seconds

@app.route('/')
def hello():
    """Main route with cluster activity dashboard"""
    space_message = random.choice(SPACE_MESSAGES)
    
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
                min-height: 100vh;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
                background-attachment: fixed;
                color: white;
                overflow-x: hidden;
            }}
            
            .command-center {{
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .title {{
                color: #00ffff;
                font-size: 2.5em;
                font-weight: 900;
                margin: 0 0 10px 0;
                text-shadow: 0 0 10px #00ffff;
                letter-spacing: 2px;
            }}
            
            .version-display {{
                display: inline-block;
                margin: 10px 0;
                padding: 8px 16px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                color: #ffffff;
                font-weight: 700;
                border-radius: 20px;
                animation: glow 2s ease-in-out infinite alternate;
            }}
            
            @keyframes glow {{
                0% {{ box-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff; }}
                100% {{ box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff; }}
            }}
            
            .dashboard {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 20px;
            }}
            
            .panel {{
                background: rgba(0, 20, 40, 0.9);
                border: 2px solid #00ffff;
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
            }}
            
            .panel h3 {{
                color: #00ffff;
                margin: 0 0 15px 0;
                font-size: 1.2em;
                text-align: center;
            }}
            
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
                margin-bottom: 15px;
            }}
            
            .metric {{
                background: rgba(0, 255, 255, 0.1);
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid rgba(0, 255, 255, 0.3);
            }}
            
            .metric-value {{
                font-size: 1.5em;
                font-weight: bold;
                color: #00ff88;
            }}
            
            .metric-label {{
                font-size: 0.8em;
                color: #ccc;
                margin-top: 5px;
            }}
            
            .events-list {{
                max-height: 300px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.85em;
            }}
            
            .event {{
                padding: 8px;
                margin: 5px 0;
                background: rgba(0, 255, 136, 0.1);
                border-left: 3px solid #00ff88;
                border-radius: 4px;
            }}
            
            .event-time {{
                color: #888;
                font-size: 0.8em;
            }}
            
            .event-message {{
                color: #00ff88;
                margin-top: 3px;
            }}
            
            .pods-grid {{
                display: grid;
                gap: 8px;
            }}
            
            .pod {{
                background: rgba(0, 255, 136, 0.1);
                padding: 10px;
                border-radius: 6px;
                border-left: 4px solid #00ff88;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            
            .pod.pending {{ border-left-color: #ffaa00; }}
            .pod.failed {{ border-left-color: #ff4444; }}
            
            .auto-refresh {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0, 255, 255, 0.2);
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                border: 1px solid #00ffff;
            }}
            
            @media (max-width: 768px) {{
                .dashboard {{ grid-template-columns: 1fr; }}
                .title {{ font-size: 1.8em; }}
            }}
        </style>
    </head>
    <body>
        <div class="auto-refresh">🔄 Auto-refresh: 5s</div>
        
        <div class="command-center">
            <div class="header">
                <div class="ship-icon" style="font-size: 2em;">🚀</div>
                <h1 class="title">STARSHIP CI/CD</h1>
                <p style="opacity: 0.8;">Command Center Online</p>
                <div class="version-display">BUILD VERSION: {APP_VERSION}</div>
                <p style="font-family: 'Courier New', monospace; color: #00ff88; margin: 10px 0;">
                    STATUS: {space_message}
                </p>
            </div>
            
            <div class="dashboard">
                <div class="panel">
                    <h3>🛸 Deployment Status</h3>
                    <div class="status-grid" id="deployment-status">
                        <div class="metric">
                            <div class="metric-value" id="replicas">-</div>
                            <div class="metric-label">Replicas</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="ready">-</div>
                            <div class="metric-label">Ready</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="updated">-</div>
                            <div class="metric-label">Updated</div>
                        </div>
                    </div>
                    <div id="current-image" style="font-family: 'Courier New', monospace; font-size: 0.8em; color: #ccc; text-align: center;">
                        Image: Loading...
                    </div>
                </div>
                
                <div class="panel">
                    <h3>🌌 Pod Status</h3>
                    <div class="status-grid" id="pod-metrics">
                        <div class="metric">
                            <div class="metric-value" id="total-pods">-</div>
                            <div class="metric-label">Total</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="running-pods">-</div>
                            <div class="metric-label">Running</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" id="pending-pods">-</div>
                            <div class="metric-label">Pending</div>
                        </div>
                    </div>
                    <div class="pods-grid" id="pods-list">
                        Loading pods...
                    </div>
                </div>
                
                <div class="panel" style="grid-column: span 2;">
                    <h3>⚡ Live Cluster Events</h3>
                    <div class="events-list" id="events-list">
                        Loading events...
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function updateDashboard() {{
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {{
                        // Update deployment status
                        const deployment = data.deployment;
                        document.getElementById('replicas').textContent = deployment.replicas || '-';
                        document.getElementById('ready').textContent = deployment.ready_replicas || '0';
                        document.getElementById('updated').textContent = deployment.updated_replicas || '0';
                        
                        if (deployment.image) {{
                            const imageTag = deployment.image.split(':')[1] || 'unknown';
                            document.getElementById('current-image').textContent = `Image: ${{imageTag}}`;
                        }}
                        
                        // Update pod status
                        const pods = data.pods;
                        document.getElementById('total-pods').textContent = pods.total || '0';
                        document.getElementById('running-pods').textContent = pods.running || '0';
                        document.getElementById('pending-pods').textContent = pods.pending || '0';
                        
                        // Update pods list
                        const podsList = document.getElementById('pods-list');
                        if (pods.pods && pods.pods.length > 0) {{
                            podsList.innerHTML = pods.pods.map(pod => 
                                `<div class="pod ${{pod.phase.toLowerCase()}}">
                                    <strong>${{pod.name}}</strong><br>
                                    Phase: ${{pod.phase}} | Ready: ${{pod.ready ? 'Yes' : 'No'}} | Restarts: ${{pod.restarts}}<br>
                                    Node: ${{pod.node}} | Age: ${{pod.age}}
                                </div>`
                            ).join('');
                        }} else {{
                            podsList.innerHTML = '<div style="color: #888;">No pods found</div>';
                        }}
                        
                        // Update events
                        const eventsList = document.getElementById('events-list');
                        if (data.events && data.events.length > 0) {{
                            eventsList.innerHTML = data.events.slice(-20).reverse().map(event => {{
                                const time = new Date(event.timestamp).toLocaleTimeString();
                                return `<div class="event">
                                    <div class="event-time">${{time}} - ${{event.namespace}}/${{event.object}}</div>
                                    <div class="event-message">${{event.reason}}: ${{event.message}}</div>
                                </div>`;
                            }}).join('');
                        }} else {{
                            eventsList.innerHTML = '<div style="color: #888;">No recent events</div>';
                        }}
                    }})
                    .catch(error => console.error('Error fetching status:', error));
            }}
            
            // Update dashboard every 5 seconds
            updateDashboard();
            setInterval(updateDashboard, 5000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.route('/api/status')
def api_status():
    """API endpoint to get current cluster status"""
    return jsonify({
        'deployment': deployment_status,
        'pods': pod_status,
        'events': cluster_events[-20:],  # Last 20 events
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

if __name__ == '__main__':
    # Initialize Kubernetes client
    k8s_client = init_kubernetes()
    
    if k8s_client:
        # Start background threads for monitoring
        threading.Thread(target=watch_cluster_events, daemon=True).start()
        threading.Thread(target=update_cluster_status, daemon=True).start()
        print("Started Kubernetes monitoring threads")
    else:
        print("Kubernetes monitoring disabled - client not available")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)
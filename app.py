import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
from rcon import Client

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

RCON_HOST = os.environ.get('RCON_HOST', 'localhost')
RCON_PORT = int(os.environ.get('RCON_PORT', 27015))
RCON_PASSWORD = os.environ.get('RCON_PASSWORD', 'changeme')

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Project Zomboid RCON Manager</title>
</head>
<body>
    <h1>Zomboid Server Manager</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
        {% for message in messages %}
          <li>{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <h2>Quick Commands</h2>
    <form method="post" action="{{ url_for('run_command') }}">
        <button type="submit" name="command" value="save">Save World</button>
        <button type="submit" name="command" value="restart">Restart Server</button>
        <button type="submit" name="command" value="stop">Stop Server</button>
    </form>

    <h2>Send Server Message</h2>
    <form method="post" action="{{ url_for('run_command') }}">
        <input type="hidden" name="command" value="say">
        <input type="text" name="message" placeholder="Your message" required>
        <button type="submit">Send Message</button>
    </form>

    <h2>Custom Command</h2>
    <form method="post" action="{{ url_for('run_command') }}">
        <input type="text" name="command" placeholder="Custom command" required>
        <button type="submit">Run</button>
    </form>
</body>
</html>

"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/command', methods=['POST'])
def run_command():
    cmd = request.form.get('command')
    if cmd == 'say':
        msg = request.form.get('message')
        full_cmd = f"say {msg}"
    else:
        full_cmd = cmd

    try:
        with Client(RCON_HOST, RCON_PORT, passwd=RCON_PASSWORD) as client:
            resp = client.run(full_cmd)
            flash(f"Command '{full_cmd}' executed. Response: {resp}")
    except Exception as e:
        flash(f"Error executing '{full_cmd}': {e}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
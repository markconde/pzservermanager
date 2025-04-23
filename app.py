import os
from flask import Flask, render_template, request, redirect, url_for, flash
from rcon import Client
from config import Config
from commands import commands

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.route('/', methods=['GET'])
    def index():
        return render_template("index.html", commands=commands)
    
    @app.route('/command', methods=['POST'])
    def run_command():
        cmd_key = request.form.get('command')
        cmd_info = commands.get(cmd_key)
        if not cmd_info:
            flash(f"Unknown command: {cmd_key}")
            return redirect(url_for('index'))
    
        # Build command string using parameters
        params = []
        for param in cmd_info['params']:
            value = request.form.get(param)
            if value:
                params.append(f'"{value}"')
        full_cmd = f"{cmd_key} " + " ".join(params) if params else f"{cmd_key}"
        
        try:
            with Client(app.config['RCON_HOST'],
                        app.config['RCON_PORT'],
                        passwd=app.config['RCON_PASSWORD']) as client:
                resp = client.run(full_cmd)
                flash(f"Command '{full_cmd}' executed. Response: {resp}")
        except Exception as e:
            flash(f"Error executing '{full_cmd}': {e}")
    
        return redirect(url_for('index'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
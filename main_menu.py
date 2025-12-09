import json
from flask import Flask, render_template
from query.route import query_bp
from decorators.access import login_required, group_required
from auth.auth_routes import auth_bp
from report.report_routes import report_bp
from ticket.ticket_routes import ticket_bp

app = Flask(__name__)
app.secret_key = 'You will never guess'

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(query_bp, url_prefix='/cinema')
app.register_blueprint(report_bp, url_prefix='/report')
app.register_blueprint(ticket_bp, url_prefix='/ticket')

with open('data/db_config.json') as f:
    app.config['db_config'] = json.load(f)

with open('data/access.json') as f:
    app.config['db_access'] = json.load(f)

@app.route('/')
@login_required
def main_menu():
    return render_template('main_menu.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5110, debug=True)


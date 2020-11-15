from flask_script import Manager, Shell, Server
from app import create_app, db
import sys

host = '127.0.0.1'
port = 5000

app = create_app()
manager = Manager(app)

def app_info():
    return dict(app=app, db=db)

manager.add_command("shell", Shell(make_context=app_info))

if __name__ == '__main__':
    app.run(debug=True)
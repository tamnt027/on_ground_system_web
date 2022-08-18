
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_admin import BaseView, expose, AdminIndexView

app = Flask('ground system')
app.secret_key = '8edf0f513be6eb81c0a72b8c28e4d2f1' #random key
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./local_database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

admin = Admin(app=app, name='System Settings', template_mode='bootstrap4', index_view=MyAdminIndexView())

login = LoginManager(app=app)

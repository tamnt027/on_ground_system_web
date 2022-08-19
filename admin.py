from unicodedata import name
from init import admin, db, login
from models import ADS, PCF8575, Lora, MasterValve, Mqtt, Pump, SeriesDisplayConfiguration, Valve, Group, User, UserRole, ScheduleTask, Chart, Sensor
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView

from flask_login import  logout_user, current_user
from flask import redirect

class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(AuthenticatedBaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    
class AuthenticatedAdminModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    edit_modal = True
    details_modal = True
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class GroupView(AuthenticatedAdminModelView):
    form_excluded_columns = ['active']


class ValveView(AuthenticatedAdminModelView):
  
    form_excluded_columns = ['active']


class UserView(AuthenticatedAdminModelView):
    can_edit = False
    
class ADSView(AuthenticatedAdminModelView):
    pass

class PCF8575View(AuthenticatedAdminModelView):
    pass
    
class MqttView(AuthenticatedAdminModelView):
    pass

class LoraView(AuthenticatedAdminModelView):
    pass

class PumpView(AuthenticatedAdminModelView):
    pass

class MasterValveView(AuthenticatedAdminModelView):
    pass

class ScheduleTaskView(AuthenticatedAdminModelView):
    pass

class ChartView(AuthenticatedAdminModelView):
    pass

class SensorView(AuthenticatedAdminModelView):
    pass

class SeriesDisplayConfigurationView(AuthenticatedAdminModelView):
    pass


    
admin.add_view(GroupView(Group, db.session, name= 'Groups' ))
admin.add_view(ValveView(Valve, db.session, name= 'Valves' ))
admin.add_view(UserView(User, db.session, name= 'Users' ))
# admin.add_view(ADSView(ADS, db.session, name= 'Ads' ))
# admin.add_view(PCF8575View(PCF8575, db.session, name= 'Pcf8575' ))
admin.add_view(MqttView(Mqtt, db.session, name= 'Mqtt' ))
admin.add_view(LoraView(Lora, db.session, name= 'Loras' ))
admin.add_view(PumpView(Pump, db.session, name= 'Pumps' ))
admin.add_view(MasterValveView(MasterValve, db.session, name= 'MasterValves' ))
admin.add_view(ScheduleTaskView(ScheduleTask, db.session, name= 'ScheduleTasks' ))
admin.add_view(SensorView(Sensor, db.session, name= 'Sensors' ))
admin.add_view(SeriesDisplayConfigurationView(SeriesDisplayConfiguration, db.session, name= 'Series Display' ))
admin.add_view(ChartView(Chart, db.session, name= 'Charts' ))
admin.add_view(LogoutView(name=f'Logout'))

# admin.add_view(ModelView(group_valve, db.session ))

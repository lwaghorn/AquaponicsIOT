import os
import sys
sys.path.append("/opt/python/current/app/homeIot")

from flask import Flask, render_template
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from controllers import cycleSettingsController, dataCollectionController, schedulerController, chartController

sys.dont_write_bytecode = True
application = Flask(__name__)
application.config.from_object(__name__)
# Nothing valuable in here anyway ;)
application.config.update(
                  SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:qZL2SDXZ7uzg@aahepsdooxe5ga.cz99kvkmqcju.ca-central-1.rds.amazonaws.com/ebdb',
                  SECRET_KEY='secret!',
                  JWT_SECRET_KEY='jwt-secret-string',
                  SQLALCHEMY_TRACK_MODIFICATIONS='false',
                  TEMPLATES_AUTO_RELOAD=True
                    )
mobileAPI = Api(application)
CORS(application)


@application.route('/')
def landing_controller():
    return render_template('landingPage.html')


mobileAPI.add_resource(schedulerController.GiveServerTime, '/API/getTime')
mobileAPI.add_resource(schedulerController.ChangeLightSchedule, '/API/test')
mobileAPI.add_resource(dataCollectionController.Collect, '/API/data')
mobileAPI.add_resource(cycleSettingsController.Change, '/API/toggleLight')
mobileAPI.add_resource(cycleSettingsController.UpdateCycleSettings, '/API/updateCycleSettings')
mobileAPI.add_resource(cycleSettingsController.GetConfiguration, '/API/getConfiguration')
mobileAPI.add_resource(cycleSettingsController.GetConfigurationAndStates, '/API/loadSettings')
mobileAPI.add_resource(cycleSettingsController.GetConfigurationArduino, '/API/GetConfigurationArduino')

mobileAPI.add_resource(chartController.TemperatureHumidity, '/API/temperatureHumidityChart')
mobileAPI.add_resource(chartController.CycleTimeRatiosChart, '/API/cycleTimeRatios')
mobileAPI.add_resource(chartController.LightTimeRatiosChart, '/API/lightTimeRatios')



from models.models import db
db.init_app(application)
migrate = Migrate(application, db)


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = False
    application.run()


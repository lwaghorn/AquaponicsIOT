from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import sys

db = SQLAlchemy()


class CycleFeedbackModel(db.Model):

	__tablename__ = 'cycle_feedback'

	id = db.Column(db.Integer, primary_key=True)
	configuration_id = db.Column(db.Integer, nullable=False)
	time_to_fill = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.DateTime, server_default=db.func.now())

	def save(self):
		db.session.add(self)
		db.session.commit()

	def log_cycle_feedback(self, time_to_fill):
		self.time_to_fill = time_to_fill
		current_configuration  = CycleConfigurationModel.get_current()
		self.configuration_id = current_configuration.get_id()
		self.save()
		return

	@staticmethod
	def get_past_feedback(days):
		model = CycleFeedbackModel
		past = datetime.now() - timedelta(days=days)
		data = model.query.filter(model.created_at >= past).all()
		return data

	@staticmethod
	def get_last_cycle():
		obj = CycleFeedbackModel
		return obj.query.order_by('-id').first()

	def get_time_to_fill(self):
		return self.time_to_fill

class LightScheduleModel(db.Model):

	__tablename__ ='light_schedules'

	id = db.Column(db.Integer, primary_key=True)
	light_id = db.Column(db.String(120), unique=True, nullable=False)
	start_time = db.Column(db.Integer, nullable=False)
	stop_time = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.DateTime, server_default=db.func.now())

	@staticmethod
	def get_from_light_id(given_id):
		obj = LightScheduleModel()
		return obj.query.filter_by(light_id = given_id).first()

	def get_start_time(self):
		return self.start_time

	def get_stop_time(self):
		return self.stop_time

	def save(self):
		db.session.add(self)
		db.session.commit()


class LightModeModel(db.Model):
	
	__tablename__ = 'light_modes'

	id = db.Column(db.Integer, primary_key=True)
	light_id = db.Column(db.Integer, unique=True, nullable=False)
	mode = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.DateTime, server_default=db.func.now())

	def save(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def reset_modes():
		lights = LightsModel.get_all()
		for light in lights:
			mode_model = LightModeModel()
			mode_model.light_id = light.get_id()
			mode_model.mode = 2
			mode_model.save()
		return

	@staticmethod
	def get_mode_from_light_id(light_id):
		model = LightModeModel()
		mode = model.query.filter_by(light_id=light_id).order_by('-id').first()
		if mode is not None:
			return mode.get_mode()
		else:
			return False

	def get_mode(self):
		return self.mode

	@staticmethod
	def log_change(light, state):
		light = LightsModel.get_light_from_name(light)
		if light is not False:
			mode_model = LightModeModel()
			mode_model.light_id = light.get_id()
			mode_model.mode = state
			mode_model.save()


class LightsModel(db.Model):
	
	__tablename__ = 'lights'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)

	def get_id(self):
		return self.id

	@staticmethod
	def get_light_from_name(name):
		model = LightsModel()
		light = model.query.filter_by(name=name).first()
		if light is not None:
			return light
		else:
			return False

	@staticmethod
	def get_all():
		obj = LightsModel()
		return obj.query.all()

	def get_status(self):
		light_schedule = LightScheduleModel.get_from_light_id(self.id)
		time = datetime.now()
		start_time = light_schedule.get_start_time()
		stop_time = light_schedule.get_stop_time()
		if time.hour > start_time and time.hour < stop_time:
			return 1
		else:
			return 0

	def get_light_schedule(self):
		return LightScheduleModel.get_from_light_id(self.id)

	def get_mode(self):
		return LightModeModel.get_mode_from_light_id(self.id)

	@staticmethod
	def get_status_dict():
		lights = LightsModel.get_all()
		response = []
		for light in lights:
			lightDict = dict()
			lightDict['lightName'] = light.name
			lightDict['status'] = light.get_status()
			lightDict['mode'] = light.get_mode()
			response.append(lightDict)
		return response


class AtmosphereModel(db.Model):

	__tablename__ = 'atmosphere'

	id = db.Column(db.Integer, primary_key=True)
	temperature = db.Column(db.Float, nullable=False)
	humidity = db.Column(db.Float, nullable=False)
	light = db.Column(db.Float, nullable=False)
	created_at = db.Column(db.DateTime, server_default=db.func.now())

	def save(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_past_feedback(days):
		model = AtmosphereModel
		# The system is no longer active so this is hard coded to a 3 day span
		# last summer where the data was good :)
		good_data = datetime(2018,7,11)
		good_data_span = good_data - timedelta(days=days)
		data = model.query.filter(model.created_at >= good_data_span).filter(model.created_at <= good_data).all()
		return data


class CycleConfigurationModel(db.Model):

	__tablename__ = 'cycle_configuration'

	id = db.Column(db.Integer, primary_key=True)
	threshold = db.Column(db.Integer, nullable=False)
	dry_time = db.Column(db.Integer, nullable=False)
	error_time = db.Column(db.Integer, nullable=False)
	drain_time = db.Column(db.Integer , nullable=False)
	dc_pulse = db.Column(db.Integer , nullable=False)

	def save(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_current():
		obj = CycleConfigurationModel()
		return obj.query.order_by('-id').first()

	def get_error_time(self):
		return self.error_time

	def get_dry_time(self):
		return self.dry_time

	def get_drain_time(self):
		return self.drain_time

	def set_cycle_settings(self, data):
		self.threshold = data['threshold']
		self.dry_time = data['dryTime']
		self.error_time = data['errorTime']
		self.drain_time = data['drainTime']
		self.dc_pulse = data['dcPulse']
		return

	def verfify_settings(self):
		return True

	def get_dict(self):
		response = dict()
		response['threshold'] = self.threshold
		response['drainTime'] = self.drain_time
		response['errorTime'] = self.error_time
		response['dryTime'] = self.dry_time
		response['dcPulse'] = self.dc_pulse
		return response

	def get_id(self):
		return self.id

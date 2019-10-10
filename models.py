import os
from dotenv import load_dotenv
from peewee import *
from datetime import datetime

APP_ROOT = os.path.join(os.path.dirname(__file__), '')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

DATABASE = MySQLDatabase(os.getenv('DB_DATABASE'),
					user=os.getenv('DB_USERNAME'),
					password=os.getenv('DB_PASSWORD'),
					host=os.getenv('DB_HOST'),
					port=int(os.getenv('DB_PORT'), 10))

class BaseModel(Model):
	class Meta:
		database = DATABASE

class Node(BaseModel):
	id = PrimaryKeyField(unique=True)
	str_SISTEMA = CharField()
	str_CENTRO_DE_CONTROL_REGIONAL = CharField()
	str_ZONA_DE_CARGA = CharField()
	str_CLAVE = CharField(unique=True)
	str_NOMBRE = CharField()
	int_NIVEL_DE_TENSION = IntegerField()
	str_ZONA_DE_OPERACION_DE_TRANSMISION = CharField()
	str_GERENCIA_REGIONAL_DE_TRANSMISION = CharField()
	str_ZONA_DE_DISTRIBUCION = CharField()
	str_GERENCIA_DIVISIONAL_DE_DISTRIBUCION = CharField()
	int_INEGI_CLAVE_ENTIDAD_FEDERATIVA = IntegerField()
	str_INEGI_ENTIDAD_FEDERATIVA = CharField()
	int_INEGI_CLAVE_MUNICIPIO = IntegerField()
	str_INEGI_MUNICIPIO = CharField()
	str_REGION_DE_TRANSMISION = CharField()

	@property
	def serialize(self):
		data = {
			'id': self.id,
			'str_SISTEMA': str(self.str_SISTEMA).strip(),
			'str_CENTRO_DE_CONTROL_REGIONAL': str(self.str_CENTRO_DE_CONTROL_REGIONAL).strip(),
			'str_ZONA_DE_CARGA': str(self.str_ZONA_DE_CARGA).strip(),
			'str_CLAVE': str(self.str_CLAVE).strip(),
			'str_NOMBRE': str(self.str_NOMBRE).strip(),
			'int_NIVEL_DE_TENSION': self.int_NIVEL_DE_TENSION,
			'str_ZONA_DE_OPERACION_DE_TRANSMISION': str(self.str_ZONA_DE_OPERACION_DE_TRANSMISION).strip(),
			'str_GERENCIA_REGIONAL_DE_TRANSMISION': str(self.str_GERENCIA_REGIONAL_DE_TRANSMISION).strip(),
			'str_ZONA_DE_DISTRIBUCION': str(self.str_ZONA_DE_DISTRIBUCION).strip(),
			'str_GERENCIA_DIVISIONAL_DE_DISTRIBUCION': str(self.str_GERENCIA_DIVISIONAL_DE_DISTRIBUCION).strip(),
			'int_INEGI_CLAVE_ENTIDAD_FEDERATIVA': self.int_INEGI_CLAVE_ENTIDAD_FEDERATIVA,
			'str_INEGI_ENTIDAD_FEDERATIVA': str(self.str_INEGI_ENTIDAD_FEDERATIVA).strip(),
			'int_INEGI_CLAVE_MUNICIPIO': self.int_INEGI_CLAVE_MUNICIPIO,
			'str_INEGI_MUNICIPIO': str(self.str_INEGI_MUNICIPIO).strip(),
			'str_REGION_DE_TRANSMISION': str(self.str_REGION_DE_TRANSMISION).strip(),
		}

		return data

	def __repr__(self):
		return "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
			self.id,
			self.str_SISTEMA,
			self.str_CENTRO_DE_CONTROL_REGIONAL,
			self.str_ZONA_DE_CARGA,
			self.str_CLAVE,
			self.str_NOMBRE,
			self.int_NIVEL_DE_TENSION,
			self.str_ZONA_DE_OPERACION_DE_TRANSMISION,
			self.str_GERENCIA_REGIONAL_DE_TRANSMISION,
			self.str_ZONA_DE_DISTRIBUCION,
			self.str_GERENCIA_DIVISIONAL_DE_DISTRIBUCION,
			self.int_INEGI_CLAVE_ENTIDAD_FEDERATIVA,
			self.str_INEGI_ENTIDAD_FEDERATIVA,
			self.int_INEGI_CLAVE_MUNICIPIO,
			self.str_INEGI_MUNICIPIO,
			self.str_REGION_DE_TRANSMISION
		)

	class Meta:
		table_name = 'tbl_nodos'

class Request_PML(BaseModel):
	id = PrimaryKeyField()
	str_SISTEMA = CharField()
	str_PROCESO = CharField()
	date_FECHA_INICIO = DateTimeField()
	date_FECHA_FIN = DateTimeField()
	created_at = DateTimeField()

	@property
	def serialize(self):
		data = {
			'id': self.id,
			'str_SISTEMA': str(self.str_SISTEMA).strip(),
			'str_PROCESO': str(self.str_PROCESO).strip(),
			'date_FECHA_INICIO': self.date_FECHA_INICIO,
			'date_FECHA_FIN': self.date_FECHA_FIN,
			'created_at': self.created_at
		}

		return data

	def __repr__(self):
		return "{}, {}, {}, {}, {}, {}".format(
			self.id,
			self.str_SISTEMA,
			self.str_PROCESO,
			self.date_FECHA_INICIO.strftime('%Y-%m-%d'),
			self.date_FECHA_FIN.strftime('%Y-%m-%d'),
			self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		)

	class Meta:
		table_name = 'tbl_peticion'

class Rel_Req_Node(BaseModel):
	id = PrimaryKeyField()
	node_id = IntegerField()
	request_id = IntegerField()
	node = ForeignKeyField(Node)
	request = ForeignKeyField(Request_PML)

	@property
	def serialize(self):
		data = {
			'id': self.id,
			'node_id': self.node_id,
			'request_id': self.request_id,
			'node': {},
			'request': {}
		}

		data['node']['id'] = self.node.id
		data['node']['str_SISTEMA'] = self.node.str_SISTEMA
		data['node']['str_CENTRO_DE_CONTROL_REGIONAL'] = self.node.str_CENTRO_DE_CONTROL_REGIONAL
		data['node']['str_ZONA_DE_CARGA'] = self.node.str_ZONA_DE_CARGA
		data['node']['str_CLAVE'] = self.node.str_CLAVE
		data['node']['str_NOMBRE'] = self.node.str_NOMBRE
		data['node']['int_NIVEL_DE_TENSION'] = self.node.int_NIVEL_DE_TENSION
		data['node']['str_ZONA_DE_OPERACION_DE_TRANSMISION'] = self.node.str_ZONA_DE_OPERACION_DE_TRANSMISION
		data['node']['str_GERENCIA_REGIONAL_DE_TRANSMISION'] = self.node.str_GERENCIA_REGIONAL_DE_TRANSMISION
		data['node']['str_ZONA_DE_DISTRIBUCION'] = self.node.str_ZONA_DE_DISTRIBUCION
		data['node']['str_GERENCIA_DIVISIONAL_DE_DISTRIBUCION'] = self.node.str_GERENCIA_DIVISIONAL_DE_DISTRIBUCION
		data['node']['int_INEGI_CLAVE_ENTIDAD_FEDERATIVA'] = self.node.int_INEGI_CLAVE_ENTIDAD_FEDERATIVA
		data['node']['str_INEGI_ENTIDAD_FEDERATIVA'] = self.node.str_INEGI_ENTIDAD_FEDERATIVA
		data['node']['int_INEGI_CLAVE_MUNICIPIO'] = self.node.int_INEGI_CLAVE_MUNICIPIO
		data['node']['str_INEGI_MUNICIPIO'] = self.node.str_INEGI_MUNICIPIO
		data['node']['str_REGION_DE_TRANSMISION'] = self.node.str_REGION_DE_TRANSMISION

		data['request']['id'] = self.request.id
		data['request']['str_SISTEMA'] = self.request.str_SISTEMA
		data['request']['str_PROCESO'] = self.request.str_PROCESO
		data['request']['date_FECHA_INICIO'] = self.request.date_FECHA_INICIO
		data['request']['date_FECHA_FIN'] = self.request.date_FECHA_FIN
		data['request']['created_at'] = self.request.created_at

		return data

	def __repr__(self):
		return "{}, {}, {}, {}, {}".format(
			self.id,
			self.node_id,
			self.request_id,
			self.node,
			self.request
		)

	class Meta:
		table_name = 'rel_nodos_peticion'

class ErrorLog(BaseModel):
	id = PrimaryKeyField(unique=True)
	str_description = CharField()
	str_extraInfo = CharField()
	ser_CLAVES = CharField()
	str_SISTEMA = CharField()
	str_PROCESO = CharField()
	date_FECHA_PETICION = DateTimeField()
	bool_resuelto = BooleanField()
	created_at = DateTimeField()
	resolved_at = DateTimeField()

	@property
	def serialize(self):
		data = {
			'id': self.id,
			'str_description': str(self.str_description).strip(),
			'str_extraInfo': str(self.str_extraInfo).strip(),
			'ser_CLAVES': str(self.ser_CLAVES).strip().split('#'),
			'str_SISTEMA': str(self.str_SISTEMA).strip(),
			'str_PROCESO': str(self.str_PROCESO).strip(),
			'date_FECHA_PETICION': self.date_FECHA_PETICION,
			'bool_resuelto': self.bool_resuelto,
			'created_at': self.created_at,
			'resolved_at': self.resolved_at
		}

		return data

	def __repr__(self):
		return "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
			self.id,
			self.str_description,
			self.str_extraInfo,
			self.ser_CLAVES,
			self.str_SISTEMA,
			self.str_PROCESO,
			self.date_FECHA_PETICION,
			self.bool_resuelto,
			self.created_at,
			self.resolved_at
		)

	class Meta:
		table_name = 'tbl_error_log'

class Estado(BaseModel):
	id = PrimaryKeyField()
	Nombre = CharField()

	@property
	def serialize(self):
		data = {
			'id': self.id,
			'Nombre': str(self.Nombre).strip()
		}
		return data

	def __repr__(self):
		return "[{}] - {}".format(self.id, self.Nombre)

	class Meta:
		table_name = 'inegi_estados'

class Municipio(BaseModel):
	id = PrimaryKeyField()
	Estado_id = IntegerField()
	Inegi_id = IntegerField()
	Nombre = CharField()

	@property
	def serialize(self):
		data = {
			'id': self.id,
			'Estado_id': self.Estado_id,
			'Inegi_id': self.Inegi_id,
			'Nombre': str(self.Nombre).strip()
		}
		return data

	def __repr__(self):
		return "{}".format(self.Nombre)

	class Meta:
		table_name = 'inegi_municipios'


DATABASE.connect()

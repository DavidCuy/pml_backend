import os
from dotenv import load_dotenv
import pymongo

class DB(object):
	APP_ROOT = os.path.join(os.path.dirname(__file__), '')   # refers to application_top
	dotenv_path = os.path.join(APP_ROOT, '.env')
	load_dotenv(dotenv_path)
	
	@staticmethod
	def init():
		client = pymongo.MongoClient(os.getenv('MONGO_URI'))
		DB.DATABASE = client[os.getenv('MONGO_DATABASE')]
    
	@staticmethod
	def insert(collection, data):
		DB.DATABASE[collection].insert(data)
        
	@staticmethod
	def find_one(collection, query):
		return DB.DATABASE[collection].find_one(query)

	@staticmethod
	def find(collection, query):
		return DB.DATABASE[collection].find() if query is None else DB.DATABASE[collection].find(query)

class PML(object):
	def __init__(self, clave, nombre, proceso, sistema, area, fecha, hora, datetime, pml, pml_ene, pml_per, pml_cng, inegi_estado, inegi_municipio, zona_carga):
		self.clave = clave
		self.nombre = nombre
		self.proceso = proceso
		self.sistema = sistema
		self.area = area
		self.fecha = fecha
		self.hora = hora
		self.datetime = datetime
		self.pml = pml
		self.pml_ene = pml_ene
		self.pml_per = pml_per
		self.pml_cng = pml_cng
		self.inegi_estado = inegi_estado
		self.inegi_municipio = inegi_municipio
		self.zona_carga = zona_carga

	@staticmethod
	def all():
		return list(DB.find('pml_data'))

	@staticmethod
	def where(query):
		return DB.find('pml_data', query=query)

	@staticmethod
	def findByClave(clave, proccess):
		return PML.where({'clave': clave, 'proceso': proccess})

	@staticmethod
	def getOneByClavel(clave, proccess):
		query = DB.find_one('pml_data', query={'clave': clave, 'proceso': proccess})
		return PML(
			clave = query['clave'],
			nombre = query['nombre'],
			proceso = query['proceso'],
			sistema = query['sistema'],
			area = query['area'],
			fecha = query['fecha'],
			hora = query['hora'],
			datetime = query['datetime'],
			pml = query['pml'],
			pml_ene = query['pml_ene'],
			pml_per = query['pml_per'],
			pml_cng = query['pml_cng']
		) if query else False

	@staticmethod
	def validateNodesAndDate(date_str, nodes):
		request = [
			{
				'$match': {
					'$and': [
						{'fecha':date_str},
						{'clave': {
							'$in': nodes
						}
						}
					]
				}
			},
			{ '$group': { '_id': '$clave' } }
		]
		pml_collection = DB.DATABASE['pml_data']
		nodes_cvl = list(pml_collection.aggregate(request))
		
		return list(map(lambda node: node['_id'], nodes_cvl))

	@staticmethod
	def groupClaveAndCount():
		request = [{
			"$group": {
				"_id": "$clave",
				"total": {
					"$sum": 1
				}
			}
		}]
		pml_collection = DB.DATABASE['pml_data']
		elements = list(pml_collection.aggregate(request))
		
		return elements
	
	@staticmethod
	def allCount():
		pml_collection = DB.DATABASE['pml_data']
		return pml_collection.count()

	@staticmethod
	def nodosM(inegi_estado, inegi_municipio, proceso, inicio, fin):
		request = [
			{
				"$match":
				{
					"inegi_estado": inegi_estado,
					"inegi_municipio": inegi_municipio,
					"proceso": proceso,
					"datetime": {
						"$gte": inicio,
						"$lt": fin
					}
				}
			},
			{ 
				"$group":
				{
					"_id": {
						"fecha": "$datetime"
					},
					"pml": { "$avg": "$pml" },
					"pml_ene": { "$avg": "$pml_ene" },
					"pml_per": { "$avg": "$pml_per" },
					"pml_cng": { "$avg": "$pml_cng" },
					"datetime": { "$first": "$datetime" },
					"fecha": { "$first": "$fecha" },
					"hora": { "$first": "$hora" }
				}
			},
			{
				"$sort": { "datetime": 1 }
			}
		]

		pml_collection = DB.DATABASE['pml_data']
		nodosM = list(pml_collection.aggregate(request))
		return nodosM

	def save(self):
		DB.insert('pml_data', data = self.json())

	def json(self):
		return {
			'clave': self.clave,
			'nombre': self.nombre,
			'proceso': self.proceso,
			'sistema': self.sistema,
			'area': self.area,
			'fecha': self.fecha,
			'hora': self.hora,
			'datetime': self.datetime,
			'pml': self.pml,
			'pml_ene': self.pml_ene,
			'pml_per': self.pml_per,
			'pml_cng': self.pml_cng,
			'inegi_estado': self.inegi_estado,
			'inegi_municipio': self.inegi_municipio,
			'zona_carga': self.zona_carga
		}
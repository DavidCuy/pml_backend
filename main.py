import os
from dotenv import load_dotenv
from flask import Flask, request, g
from flask_cors import CORS
import models
from datetime import datetime
from datetime import timedelta
import json, requests
from pml_storage import PML, DB

APP_ROOT = os.path.join(os.path.dirname(__file__), '')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

PML_ENDPOINT = os.getenv('CENACE_URI')

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
DB.init()

def customConverter(o):
	if isinstance(o, datetime):
		return o.__str__()

def responseJson(data, statusCode):
	return app.response_class(
        response=json.dumps(data, default = customConverter),
        status=statusCode,
        mimetype='application/json'
    )

@app.before_request
def before_request():
	""" Conecta a la base de datos antes de cada request """
	if not hasattr(g, 'db'):
		g.db = models.DATABASE
		g.db.connect()

@app.after_request
def after_request(response):
	""" Cerramos la conexion a la base de datos"""
	g.db.close()
	return response

@app.route('/api/v1/nodes', methods=['GET'])
def all_nodes():
	query = models.Node.select()
	nodes = [i.serialize for i in query]
	response = responseJson(nodes, 200)
	return response

@app.route('/api/v1/nodes/<int:id>', methods=['GET'])
def node_by_id(id):
	query = models.Node.get_by_id(id)
	node = query.serialize
	response = responseJson(node, 200)
	return response

@app.route('/api/v1/validateRequest/deprecated', methods=['POST'])
def validate_request_dep():
	params = request.json
	beginDate = datetime.strptime(params['beginDate'], '%Y-%m-%d')
	endDate = datetime.strptime(params['endDate'], '%Y-%m-%d')
	nodes = params['nodes']

	# Se prepara un arreglo con los parametros de las peticiones al servidor PML
	preppend_requests = []
	# Se recorre cada node de la peticion
	for nodeId in nodes:
		# Se optiene las peticiones anteriores relacionadas con el Nodo, esto con el fin de obtener las fechas
		query = models.Rel_Req_Node.select().join(models.Node).where(models.Node.id == nodeId)
		queryNode = models.Node.get_by_id(nodeId)
		node_ser = queryNode.serialize

		# Se prepara una nueva peticion
		new_request = {
			'node_id': node_ser['id'],
			'node_CLAVE': node_ser['str_CLAVE']
		}

		# Se crea el intervalo de la peticion, que se le ira quitando los intervalos mezclados con las peticiones anteriores
		intervals = [{
			'beginDate': beginDate,
			'endDate': endDate
		}]
		
		# Se define una bander que indica si las fechas esta en un intervalo
		is_in_interval = False

		# Se recorre cada elemento peticion pasada relacionada con el nodo actual de la iteracion
		for rel_node_req_query in query:
			# Se serializa el objeto para poder usarlo como diccionario
			rel_node_req = rel_node_req_query.serialize

			# Si el nodo aun noo tiene peticiones
			if (len(rel_node_req) > 0):
				# Se recorre cada parametro del intervalo, esto es con el fin de obtener los intervalos que se deben hacer por cada nodo, sin repetir fechas
				for interval in intervals:
					# Si la fecha de inicio del actual intervalo es menor de la iteracion actual de la peticion del elemento
					if interval['beginDate'] < rel_node_req['request']['date_FECHA_INICIO']:
						if interval['endDate'] < rel_node_req['request']['date_FECHA_INICIO']:
							pass
						# Si la fecha de fin del acutal intervalo es menor que la fecha de fin de la peticion de la iteracion (fecha de fin de intervalo entre las fechas de la peticion)
						elif interval['endDate'] < rel_node_req['request']['date_FECHA_FIN']:
							# Se cambia la fecha de fin del actual intervalo por la fecha de inicio de la peticion menos un dia
							interval['endDate'] = rel_node_req['request']['date_FECHA_INICIO'] - timedelta(days=1)
						# Si la fecha de fin del acutal intervalo es mayor que la fecha de fin de la peticion de la iteracion (fecha de fin de intervalo fuera de las fechas de la peticion)
						elif interval['endDate'] > rel_node_req['request']['date_FECHA_FIN']:
							# Se crea un nuevo intervalo con fecha de inicio igual a la fecha de inicio de la actual iteracion
							# y con fecha de fin igual al fin del actual intervalo
							intervals.append({
								'beginDate': rel_node_req['request']['date_FECHA_FIN'] + timedelta(days=1),
								'endDate': interval['endDate']
							})
							# Se cambia la fecha de fin del actual intervalo por la fecha de inicio menos un dia de la fecha de peticion de la iteracion
							interval['endDate'] = rel_node_req['request']['date_FECHA_INICIO'] - timedelta(days=1)
					# Si la fecha de inicio del acutal intervalo es menor que la fecha de fin de la peticiion de la iteracion
					elif interval['beginDate'] < rel_node_req['request']['date_FECHA_FIN']:
						# Si la fecha fin del intervalo es menor que la fecha de fin de la peticion de la iteracion
						if endDate <= rel_node_req['request']['date_FECHA_FIN']:
							is_in_interval = True
							continue
						# Si la fecha de fin de la peticion de la iteracion es menor que la fecha de fin del actual intervalo
						elif rel_node_req['request']['date_FECHA_FIN'] < interval['endDate']:
							# Se cambia la fecha de fin del actual intervalo por la fecha de final de la peticion de la iteracion mas un dia
							interval['beginDate'] = rel_node_req['request']['date_FECHA_FIN'] + timedelta(days=1)
					# Si la fecha de fin de la peticion de la iteracion es menos que la fecha de inicio
					elif rel_node_req['request']['date_FECHA_FIN'] < beginDate:
						pass
		
		# Se agrega el nuevo intervalo del nodo a la nueva peticion
		new_request['intervals'] = [] if is_in_interval else intervals
		preppend_requests.append(new_request)

	response = responseJson(preppend_requests, 200)
	
	return response

@app.route('/api/v1/validateRequest', methods=['POST'])
def validate_request():
	params = request.json
	beginDate = datetime.strptime(params['beginDate'], '%Y-%m-%d')
	endDate = datetime.strptime(params['endDate'], '%Y-%m-%d')
	node_claves = params['nodes']

	requests_pml = []
	for add_day in range(0 ,(endDate - beginDate).days + 1):
		curr_date = beginDate + timedelta(days=add_day)
		str_date = curr_date.strftime('%Y-%m-%d')
		nodes_repeated = PML.validateNodesAndDate(str_date, node_claves)
		current_claves = list(filter(lambda node: node not in nodes_repeated, node_claves))
		
		if len(current_claves) > 0:
			requests_pml.append({
				'sistema': params['system'],
				'proceso': params['proccess'],
				'beginDate': str_date,
				'endDate': str_date,
				'nodos': current_claves
			})

	response = responseJson(requests_pml, 200)
	return response

@app.route('/api/v1/prepareRequest', methods=['POST'])
def prepare_request():
	params = request.json
	beginDate = datetime.strptime(params['beginDate'], '%Y-%m-%d')
	endDate = datetime.strptime(params['endDate'], '%Y-%m-%d')
	node_claves = params['nodes']

	requests_pml = []
	for add_day in range(0 ,(endDate - beginDate).days + 1):
		curr_date = beginDate + timedelta(days=add_day)
		str_date = curr_date.strftime('%Y-%m-%d')
		requests_pml.append({
			'sistema': params['system'],
			'proceso': params['proccess'],
			'beginDate': str_date,
			'endDate': str_date,
			'nodos': node_claves
		})

	response = responseJson(requests_pml, 200)
	return response

@app.route('/api/v1/pmlRequest', methods=['POST'])
def pml_request():
	params = request.json
	beginDate = datetime.strptime(params['beginDate'], '%Y-%m-%d')
	endDate = datetime.strptime(params['endDate'], '%Y-%m-%d')
	full_nodes = params['nodos']
	nodes = list(map(lambda node: node['str_CLAVE'], full_nodes))

	if len(full_nodes) > 20:
		# Error log
		query = models.ErrorLog.create(
			str_description = 'La peticion tiene más de 20 nodos',
			str_extraInfo = '',
			ser_CLAVES = '#'.join(nodes),
			str_SISTEMA = params['sistema'],
			str_PROCESO = params['proceso'],
			date_FECHA_PETICION = params['beginDate']
		)
		response = responseJson({
			'success': False,
			'error': True,
			'description': 'La peticion tiene más de 20 nodos',
			'request': params
		}, 400)
		return response
	
	url = '{}/SWPML/SIM/{}/{}/{}/{}/{}/JSON'.format(
		PML_ENDPOINT,
		params['sistema'],
		params['proceso'],
		','.join(nodes),
		beginDate.strftime("%Y/%m/%d"),
		endDate.strftime("%Y/%m/%d")
	)
	print(url)

	resp_req = requests.get(url)
	
	if resp_req.status_code != 200:
		# Error Log
		query = models.ErrorLog.create(
			str_description = 'Error en la petición al servidor de CENACE',
			str_extraInfo = resp_req.text,
			ser_CLAVES = '#'.join(nodes),
			str_SISTEMA = params['sistema'],
			str_PROCESO = params['proceso'],
			date_FECHA_PETICION = params['beginDate']
		)
		response = responseJson({
			'success': False,
			'error': True,
			'description': 'Error en la petición al servidor de CENACE',
			'extra': resp_req.text,
			'request': params
		}, 500)
		return response
	request_response = json.loads(resp_req.content)
	print(request_response['status'])

	if request_response['status'] != "OK":
		# Error Log
		query = models.ErrorLog.create(
			str_description = 'No existen valores para los nodos solicitados',
			str_extraInfo = resp_req.text,
			ser_CLAVES = '#'.join(nodes),
			str_SISTEMA = params['sistema'],
			str_PROCESO = params['proceso'],
			date_FECHA_PETICION = params['beginDate']
		)
		response = responseJson({
			'success': False,
			'error': True,
			'description': 'No existen valores para los nodos solicitados',
			'request': params
		}, 204)
		return response

	pml_request_data = []
	for data in request_response['Resultados']:
		for value in data['Valores']:
			currentNode_list = list(filter(lambda node: node['str_CLAVE'] == data['clv_nodo'], full_nodes))
			currentNode = currentNode_list[0] if len(currentNode_list) > 0 else False
			str_datetime = "{} {}:00".format(value['fecha'], 0 if int(value['hora']) is 24 else value['hora'])
			node_datetime = datetime.strptime(str_datetime, '%Y-%m-%d %H:%M')
			pml_data = PML(data['clv_nodo'],
							request_response['nombre'],
							request_response['proceso'],
							request_response['sistema'],
							request_response['area'],
							value['fecha'],
							value['hora'],
							node_datetime,
							float(value['pml']),
							float(value['pml_ene']),
							float(value['pml_per']),
							float(value['pml_cng']),
							currentNode['int_INEGI_CLAVE_ENTIDAD_FEDERATIVA'],
							currentNode['int_INEGI_CLAVE_MUNICIPIO'],
							currentNode['str_ZONA_DE_CARGA']
			)
			pml_request_data.append(pml_data.json())
			pml_data.save()

	response = responseJson({
		'success': True,
		'error': False,
		'description': 'Datos almacenados correctamente'
	}, 200)
	return response

@app.route('/api/v1/getStorageData', methods=['GET'])
def getStorageData():
	total = PML.allCount()
	query = models.Node.select()
	nodes = [node.serialize for node in query]

	response = responseJson({
		'total': total,
		'resume': nodes,
		'nodes': nodes
	}, 200)
	return response

@app.route('/api/v1/getDataQuery', methods=['POST'])
def getDataQuery():
	params = request.json
	query = list(PML.where(params))
	response = responseJson(query, 200)
	return response

@app.route('/api/v1/errorLog/beginDate/<string:beginDate>/endDate/<string:endDate>')
def getErrorLog(beginDate, endDate, methods=['GET']):
	bDate = datetime.strptime(beginDate, '%Y-%m-%d')
	eDate = datetime.strptime(endDate, '%Y-%m-%d')
	query = models.ErrorLog.select().where((models.ErrorLog.date_FECHA_PETICION >= bDate) &
											(models.ErrorLog.date_FECHA_PETICION <= eDate))
	errors = [i.serialize for i in query]
	response = responseJson(errors, 200)
	return response


@app.route('/api/v1/inegi/estados', methods=['GET'])
def get_estados():
	query =  list(models.Estado.select())
	estados = [i.serialize for i in query]
	response = responseJson(estados, 200)
	return response

@app.route('/api/v1/inegi/estados/<int:id>/municipios', methods=['GET'])
def get_municipios_por_estado(id):
	query =  models.Municipio.select().where(models.Municipio.Estado_id == id)
	municipios = [i.serialize for i in query]
	response = responseJson(municipios, 200)
	return response

@app.route('/api/v1/nodosM', methods=['POST'])
def process_nodosM():
	params = request.json
	beginDate = datetime.strptime(params['inicio'], '%Y-%m-%d')
	endDate = datetime.strptime(params['fin'], '%Y-%m-%d')

	nodosM = PML.nodosM(params['estado'], params['municipio'], params['proceso'], beginDate, endDate)
	response = responseJson(nodosM, 200)
	return response


@app.route('/closeconnection')
def close_connection():
	g.db.close()
	return 'success'

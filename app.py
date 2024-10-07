from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL  # Asegúrate de tener flask_mysqldb instalado
import mysql.connector
import random
from deap import base, creator, tools, algorithms

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto por una clave secreta adecuada

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'guardia'

# Inicializa MySQL
mysql = MySQL(app)

# Ruta de inicio
@app.route('/')
def index():
    # Renderiza el menú principal
    return render_template('index.html')

# Ruta para registrar un estudiante
@app.route('/registrar_estudiante', methods=['POST'])
def registrar_estudiante():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    carrera_id = request.form['carrera_id']
    semestre = request.form['semestre']
    
    # Verificar si el estudiante ya existe
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM estudiante WHERE nombre = %s AND apellido = %s', (nombre, apellido))
    estudiante = cursor.fetchone()

    if estudiante:
        flash('El estudiante ya existe.', 'error')
        return redirect(url_for('register_student'))

    # Registrar nuevo estudiante
    cursor.execute('INSERT INTO estudiante (nombre, apellido, carrera_id, semestre) VALUES (%s, %s, %s, %s)',
                   (nombre, apellido, carrera_id, semestre))
    mysql.connection.commit()
    cursor.close()

    flash('¡Estudiante registrado exitosamente!', 'success')
    return redirect(url_for('register_student'))

@app.route('/modificar_estudiante', methods=['POST'])
def modificar_estudiante():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    carrera_id = request.form['carrera_id']
    semestre = request.form['semestre']

    # Modificar el estudiante en la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE estudiante SET apellido = %s, carrera_id = %s, semestre = %s WHERE nombre = %s',
                   (apellido, carrera_id, semestre, nombre))
    mysql.connection.commit()
    cursor.close()

    flash('¡Estudiante modificado exitosamente!', 'success')
    return redirect(url_for('register_student'))

@app.route('/eliminar_estudiante', methods=['POST'])
def eliminar_estudiante():
    nombre = request.form['nombre']
    apellido = request.form['apellido']

    # Eliminar el estudiante de la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM estudiante WHERE nombre = %s AND apellido = %s', (nombre, apellido))
    mysql.connection.commit()
    cursor.close()

    flash('¡Estudiante eliminado exitosamente!', 'success')
    return redirect(url_for('register_student'))

# Ruta para cargar el formulario de registro de estudiantes
@app.route('/register_student', methods=['GET'])
def register_student():
    return render_template('register_student.html', carreras=get_carreras())

# Obtener las carreras de la base de datos
def get_carreras():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_carrera, nombre_carrera FROM carrera")
    carreras = cursor.fetchall()
    cursor.close()
    return carreras

# Ruta para asignar guardias
@app.route('/asignacion_guardias', methods=['GET', 'POST'])
def asignacion_guardias():
    resultados = []
    if request.method == 'POST':
        # Aquí se implementa la lógica del algoritmo genético
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # Función para generar un individuo aleatorio
        def create_individual():
            return [random.randint(2, 5) for _ in range(6)]

        # Función de evaluación (fitness)
        def eval_individual(individual):
            return sum(individual),  # Retorna la suma como una tupla

        # Registrar los métodos en el toolbox
        toolbox = base.Toolbox()
        toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", eval_individual)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # Configuración de la población
        population = toolbox.population(n=100)

        # Ejecutar el algoritmo genético
        NGEN = 40  # Número de generaciones
        CXPB = 0.5  # Probabilidad de cruce
        MUTPB = 0.2  # Probabilidad de mutación

        # Algoritmo evolutivo
        algorithms.eaSimple(population, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, verbose=False)

        # Simulamos la asignación de estudiantes a roles para mostrar en la tabla
        for ind in population:
            # Simulamos la creación de resultados
            resultados.append({
                'nombre': f'Estudiante {random.randint(1, 100)}',
                'rol': 'Comandante' if ind[0] == 8 else 'Sargento' if ind[1] == 7 else 'Guardia',
                'semestre': ind[0]  # Simula el semestre a partir del individuo
            })

        flash('Guardias asignados exitosamente!', 'success')
        return render_template('asignacion_guardias.html', resultados=resultados)

    return render_template('asignacion_guardias.html', resultados=resultados)

if __name__ == "__main__":
    app.run(debug=True, port=5000)



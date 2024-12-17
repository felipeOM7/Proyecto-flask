from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'


conexion = mysql.connector.connect(user='root', password='root',
                                   host='localhost',
                                   database='brafel',
                                   port='3306')
if conexion.is_connected():
    print("Conexión exitosa a MySQL")


@app.route('/')
def inicio():
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM productos WHERE stock > 0')
        productos = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'Error al cargar los productos: {e}', 'danger')
        productos = []
    finally:
        cursor.close()

    return render_template('inicio.html', productos=productos)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        try:
            cursor = conexion.cursor()
            cursor.execute('INSERT INTO usuarios (nombre, correo, contraseña, rol) VALUES (%s, %s, %s, "cliente")',
                           (nombre, correo, generate_password_hash(contraseña)))
            conexion.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect('/login')
        except mysql.connector.Error as e:
            flash(f'Error al registrarse: {e}', 'danger')
        finally:
            cursor.close()

    return render_template('registro.html')

# Ruta: Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario = cursor.fetchone()
        finally:
            cursor.close()

        if usuario and check_password_hash(usuario['contraseña'], contraseña):
            session['id'] = usuario['id']
            session['nombre'] = usuario['nombre']
            session['rol'] = usuario['rol']
            flash('Inicio de sesión exitoso!', 'success')
            return redirect('/')
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')

# Ruta: Agregar producto al carrito
@app.route('/carrito/agregar', methods=['POST'])
def agregar_carrito():
    if 'id' not in session:
        flash('Debes iniciar sesión para agregar productos al carrito.', 'warning')
        return redirect('/login')

    producto_id = request.form['producto_id']
    cantidad = int(request.form['cantidad'])

    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar si hay un carrito activo
        cursor.execute('SELECT * FROM carritos WHERE usuario_id = %s AND estado = "activo"', (session['id'],))
        carrito = cursor.fetchone()

        if not carrito:
            # Crear un carrito si no existe
            cursor.execute('INSERT INTO carritos (usuario_id, estado, fecha_creacion) VALUES (%s, "activo", NOW())',
                           (session['id'],))
            conexion.commit()
            carrito_id = cursor.lastrowid
        else:
            carrito_id = carrito['id']

        # Verificar si el producto ya está en el carrito
        cursor.execute('SELECT * FROM carrito_productos WHERE carrito_id = %s AND producto_id = %s',
                       (carrito_id, producto_id))
        producto_en_carrito = cursor.fetchone()

        if producto_en_carrito:
            # Actualizar la cantidad
            nueva_cantidad = producto_en_carrito['cantidad'] + cantidad
            cursor.execute('UPDATE carrito_productos SET cantidad = %s WHERE id = %s',
                           (nueva_cantidad, producto_en_carrito['id']))
        else:
            # Agregar el producto al carrito
            cursor.execute('INSERT INTO carrito_productos (carrito_id, producto_id, cantidad) VALUES (%s, %s, %s)',
                           (carrito_id, producto_id, cantidad))

        conexion.commit()
        flash('Producto agregado al carrito.', 'success')

    except mysql.connector.Error as e:
        flash(f'Error al agregar el producto al carrito: {e}', 'danger')

    finally:
        cursor.close()

    return redirect('/')

# Ruta: Ver carrito
@app.route('/carrito')
def ver_carrito():
    if 'id' not in session:
        flash('Debes iniciar sesión para ver tu carrito.', 'warning')
        return redirect('/login')

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('''
            SELECT cp.id AS carrito_producto_id, p.nombre, p.precio, cp.cantidad, (p.precio * cp.cantidad) AS total
            FROM carrito_productos cp
            JOIN productos p ON cp.producto_id = p.id
            JOIN carritos c ON cp.carrito_id = c.id
            WHERE c.usuario_id = %s AND c.estado = "activo"
        ''', (session['id'],))
        productos = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'Error al cargar el carrito: {e}', 'danger')
        productos = []
    finally:
        cursor.close()

    return render_template('carrito.html', productos=productos)

# Ruta: Finalizar compra
@app.route('/carrito/finalizar', methods=['POST'])
def finalizar_compra():
    if 'id' not in session:
        flash('Debes iniciar sesión para finalizar la compra.', 'warning')
        return redirect('/login')

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM carritos WHERE usuario_id = %s AND estado = "activo"', (session['id'],))
        carrito = cursor.fetchone()

        if not carrito:
            flash('No tienes productos en tu carrito.', 'info')
            return redirect('/')

        carrito_id = carrito['id']

        # Crear un pedido
        cursor.execute('INSERT INTO pedidos (usuario_id, fecha_creacion) VALUES (%s, NOW())', (session['id'],))
        pedido_id = cursor.lastrowid

        # Mover los productos del carrito al pedido
        cursor.execute('''
            INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad)
            SELECT %s, producto_id, cantidad FROM carrito_productos WHERE carrito_id = %s
        ''', (pedido_id, carrito_id))

        # Actualizar stock de productos
        cursor.execute('''
            UPDATE productos p
            JOIN carrito_productos cp ON p.id = cp.producto_id
            SET p.stock = p.stock - cp.cantidad
            WHERE cp.carrito_id = %s
        ''', (carrito_id,))

        # Cambiar el estado del carrito
        cursor.execute('UPDATE carritos SET estado = "finalizado" WHERE id = %s', (carrito_id,))
        conexion.commit()

        flash('Compra finalizada exitosamente.', 'success')

    except mysql.connector.Error as e:
        flash(f'Error al finalizar la compra: {e}', 'danger')

    finally:
        cursor.close()

    return redirect('/')



@app.route('/carrito/completar_compra', methods=['POST'])
def completar_compra():
    if 'id' not in session:
        flash('Debes iniciar sesión para completar la compra.', 'warning')
        return redirect('/login')

    carrito_id = request.form.get('carrito_id')
    total = request.form.get('total')
    metodo_pago = request.form.get('metodo_pago')
    direccion_envio = request.form.get('direccion_envio')

    try:
        cursor = conexion.cursor()

        # Crear el pedido
        estado = 'Pendiente'  # Estado inicial del pedido
        cursor.execute('''
            INSERT INTO pedidos (usuario_id, total, metodo_pago, estado, direccion_envio, fecha_pedido)
            VALUES (%s, %s, %s, %s, %s, NOW())
        ''', (session['id'], total, metodo_pago, estado, direccion_envio))
        pedido_id = cursor.lastrowid

        # Mover los productos del carrito al pedido
        cursor.execute('''
            INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad)
            SELECT %s, producto_id, cantidad FROM carrito_productos WHERE carrito_id = %s
        ''', (pedido_id, carrito_id))

        # Actualizar stock de productos
        cursor.execute('''
            UPDATE productos p
            JOIN carrito_productos cp ON p.id = cp.producto_id
            SET p.stock = p.stock - cp.cantidad
            WHERE cp.carrito_id = %s
        ''', (carrito_id,))

        # Cambiar el estado del carrito
        cursor.execute('UPDATE carritos SET estado = "finalizado" WHERE id = %s', (carrito_id,))
        conexion.commit()

        flash('Compra completada exitosamente.', 'success')
        return redirect('/')

    except mysql.connector.Error as e:
        flash(f'Error al completar la compra: {e}', 'danger')
        conexion.rollback()

    finally:
        cursor.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    

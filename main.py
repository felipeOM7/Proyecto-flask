from flask import Flask 
from flask import render_template, request, redirect, flash, session
from flask import send_from_directory
from flask import flash
import mysql.connector
from datetime import datetime
import bcrypt 
from flask import Flask, jsonify

import os

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta' 



conexion = mysql.connector.connect(user='root', password='root',
                                   host='localhost',
                                   database = 'brafel',
                                   port='3306')

if conexion.is_connected():
    print("Conexión exitosa a MySQL")
    



@app.route('/')
def inicio():
    print("Conexion exitosa MySQL")
    return render_template('index.html')

@app.route('/products')
def productos_index():
    
    return render_template('product.html')

@app.route('/catalogo')
def catalogo():
    
    cursor = conexion.cursor(dictionary=True)
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    print('Conexion exitosa')
    print(productos)
    cursor.close()
    
    return render_template('/sitio/Catalogo.html', productos = productos)

@app.route('/sitio/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        correo = request.form['txtCorreo']
        contraseña = request.form['txtPassword']
        print('Correo obtenido: ', correo)
        print('Contraseña obtenida: ',contraseña)
        

        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
        usuario=cursor.fetchone()
        cursor.close()

        if usuario:
            if bcrypt.checkpw(contraseña.encode('utf-8'), usuario['contraseña'].encode('utf-8')):
                session['id'] = usuario['id']
                session['nombre'] = usuario['nombre']
                session['rol'] = usuario['rol']
                flash('Inicio de sesión exitoso!', 'success')
                return redirect('/cliente/inicio_cliente')
            else:
                 flash('Contraseña incorrecta. Intenta de nuevo.', 'danger')    
        else:
            flash('Correo no registrado. Intenta de nuevo o regístrate.', 'danger')     



    return render_template('/sitio/login.html')

@app.route('/sitio/registro', methods=['GET', 'POST'])
def registro():


    if request.method == 'POST':
        nombre = request.form['txtNombre']
        correo = request.form['txtCorreo']
        contraseña = request.form['txtPassword']
        rol = request.form['rol']

        print(f"Datos recibidos: {nombre}, {correo}, {rol}")
        try:
            
           
            hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

            
            
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("INSERT INTO usuarios (nombre, correo, contraseña, rol) VALUES (%s, %s, %s, %s)", 
                           (nombre, correo, hashed_password, rol))
            print("Conexión exitosa:", conexion.is_connected())
            flash('Usuario registrado exitosamente!', 'success') 
            conexion.commit()
            
            return redirect('/sitio/login')
        except mysql.connector.Error as e:
            flash(f'Error al registrar el usuario: {e}', 'danger')
            print(f'Error al insertar el usuario: {e}')
            return redirect('/sitio/registro')

        

     
    return render_template('/sitio/registro.html')


@app.route('/cliente/inicio_cliente')
def cliente_inicio():

    return render_template('/cliente/inicio_cliente.html')


@app.route('/admin/admin_inicio')
def admin_inicio():
    return render_template('/admin/admin_inicio.html')


@app.route('/img/<imagen>')
def imagenes(imagen):
    img_directory = os.path.join(os.getcwd(), 'static', 'img')
    print("Directorio de imágenes:", img_directory)  
    return send_from_directory(img_directory, imagen)


@app.route('/admin/Pedidos')
def pedidos_admin():
    pedido = []
    
    try:
        
        
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM `pedidos`')
        pedido = cursor.fetchall()
        print(pedido)
        conexion.commit()
        
        
        
    except mysql.connector.Error as err:
        print(f'Error de conexion: {err}')    
    

    return render_template('/admin/Pedidos.html', pedidos = pedido)    

@app.route('/admin/Pedidos/finalizado', methods=['POST'])
def pedidos_finalizado():
    
    pedido_id = request.form.get('id')
    
    
    if not pedido_id:
        
        return 'Error, falta ID del pedido', 400
    
    try: 
        
        
        
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM pedidos WHERE id = %s', (pedido_id,))
        pedido = cursor.fetchone()
        
        
        if not pedido:
            
            return 'Pedido con ID: {pedido_id}, no encontrado', 404
        
        
        
        cursor.execute('UPDATE pedidos SET estado = %s WHERE id = %s', ('entregado', pedido_id))
        
        conexion.commit()
    
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    
    finally:
        cursor.close()
        
    return redirect('/admin/Pedidos')
    
@app.route('/admin/Pedidos/cancelar', methods = ['POST'])
def pedido_cancelado():
    
    pedido_id = request.form.get('id')
    
    if not pedido_id:
        
        return 'Falta ID del pedido'
    
    try:
        
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM pedidos WHERE id = %s', (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido: 
            
            return 'El pedido no existe', 404
        
        cursor.execute('UPDATE pedidos SET estado = %s WHERE id = %s', ('cancelado', pedido_id))
        conexion.commit()
        
        
    except mysql.connector.Error as err:
        
        print('Error en el sistema : {err}') 
        
    finally:
        cursor.close()   
    
    return redirect('/admin/Pedidos')
    


@app.route('/admin/Productos')
def admin_productos():

    lista_productos = []
    categoria = []
    
    try:

      cursor = conexion.cursor(dictionary=True)
      cursor.execute('SELECT * FROM  `productos` ')
      lista_productos = cursor.fetchall()
      
      cursor.execute("SELECT * FROM categorias")
      categoria = cursor.fetchall()
      print(lista_productos)
      conexion.commit()
      print('Conexion exitosa: ', conexion.is_connected())
    
    except mysql.connector.Error as err:
        print('Error de conexion: ', err)
    
   
    
    return render_template('/admin/Productos.html', producto = lista_productos, categoria = categoria)



@app.route('/admin/productos/guardar', methods=['GET', 'POST'])
def admin_productos_save():

    _nombre = request.form['txtNombre']
    _descripcion = request.form['txtDescripcion']
    _precio = request.form['txtPrecio']
    _stock = request.form['txtStock']
    _categoria = request.form['txtCategoria']
    _imagen = request.files['imgImage']


    fecha_actual = datetime.now()
    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M')
    
    nuevoNombre = None

    if _imagen.filename!="":
        nuevoNombre = horaActual+"_"+_imagen.filename
        _imagen.save("static/img/"+ nuevoNombre)

    sql = '''
            INSERT INTO productos(nombre, descripcion, precio, stock, categoria_id, imagen_url, fecha_creacion, fecha_actualizacion)
             VALUES(%s, %s, %s, %s, %s, %s, %s, %s) 
    
    
    '''

    datos = (_nombre, _descripcion, _precio, _stock, _categoria, nuevoNombre if nuevoNombre else None, fecha_actual, fecha_actual)



    try:
         cursor = conexion.cursor()
         cursor.execute(sql, datos)
         conexion.commit()
    except mysql.connector.Error as err:
        print(f"Error al conectar BD: {err}")


    finally:
        cursor.close()

    print(_nombre, _descripcion, _precio, _stock, _categoria, _imagen)

    return redirect('/admin/Productos')



@app.route('/admin/Productos/borrar', methods =['POST'])
def admin_products_delete():
    _id = request.form['txtID']
    print(_id)

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT imagen_url FROM productos WHERE id = %s",(_id,))
    producto = cursor.fetchall()
    conexion.commit()
    print(producto)

    if os.path.exists("static/img/"+str(producto[0]['imagen_url'])):
        os.unlink("static/img/"+str(producto[0]['imagen_url']))
    
    
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("DELETE FROM productos WHERE id=%s",(_id,))
    conexion.commit()

    return redirect('/admin/Productos')


@app.route('/admin/Productos/editar', methods=['POST'])
def admin_products_edit():

    _id = request.form['txtID']
    
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id = %s", (_id,))
    producto = cursor.fetchone()
    cursor.close()

    if producto: 
        return render_template('/admin/editar_producto.html', producto = producto)
    else: 
        flash('Producto no encontrado', 'danger')
        return redirect('/admin/Productos')

@app.route('/admin/Productos/actualizar', methods=['POST'])
def actualizar_producto():
    id = request.form['txtID']
    nombre = request.form['txtNombre']
    descripcion = request.form['txtDescripcion']
    precio = request.form['txtPrecio']
    stock = request.form['txtStock']
    categoria = request.form['txtCategoria']
    imagen = request.files['imgImage']

    cursor = conexion.cursor()

    fecha_actual = datetime.now()
    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M')

    if imagen.filename !='':
        
        nuevoNombre = horaActual+"_"+ imagen.filename
        imagen.save("static/img/"+ nuevoNombre)
    
        cursor.execute('''
                UPDATE productos 
                SET nombre=%s, descripcion=%s, precio=%s, stock=%s, categoria_id=%s, imagen_url=%s,fecha_actualizacion=%s 
                WHERE id=%s
            ''', (nombre, descripcion, precio, stock, categoria, nuevoNombre, fecha_actual, id))
    else:
        cursor.execute('''
            UPDATE productos 
            SET nombre=%s, descripcion=%s, precio=%s, stock=%s, categoria_id=%s, fecha_actualizacion=%s 
            WHERE id=%s
        ''', (nombre, descripcion, precio, stock, categoria, fecha_actual, id))

    conexion.commit()
    cursor.close()

    flash('Producto actualizado exitosamente', 'success')
    return redirect('/admin/Productos')

@app.route('/admin/categoria/agregar', methods=['GET','POST'])
def categoria_guardar():
    
     
    return render_template('/admin/categoria.html')


@app.route('/admin/categoria/guardar', methods=['POST'])
def categoria_save():
    if request.method == 'POST':
        
        _nombre = request.form['txtNombre']
        _descripcion = request.form['txtDescripcion']
        
        fecha_actual = datetime.now()
     
        sql = '''
            INSERT INTO categorias(nombre, descripcion, fecha_creacion)
            VALUES(%s, %s, %s)


          '''

        datos = (_nombre, _descripcion, fecha_actual)

        try:
            cursor = conexion.cursor()
            cursor.execute(sql, datos)
            conexion.commit()


        except mysql.connector.Error as err:
            print(f'Error al conectar BD' +{err})  
        
        finally:
            cursor.close()

        print(_nombre, _descripcion, fecha_actual)

        return redirect('/admin/Productos')

@app.route('/admin/categoria/editar', methods=['POST'])
def admin_categoria_editar():
    
    _id = request.form['txtID']
    
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias WHERE id = %s", (_id,))
    categoria =  cursor.fetchone()
    cursor.close()
    
    if categoria:
        return render_template('/admin/editar_categoria.html', categoria = categoria)
    
    else: 
        flash('Categoria no encontrada', 'danger')
        return redirect('/admin/Productos')
    

@app.route('/admin/categoria/actualizar', methods=['POST'])
def update_category(): 
    _id = request.form['txtID']
    _nombre = request.form['txtNombre']
    _descripcion = request.form['txtDescripcion']
    
    cursor = conexion.cursor()
    
    
    fecha_actual = datetime.now()
    
    
    cursor.execute('''
                UPDATE categorias 
                SET nombre=%s, descripcion=%s, fecha_creacion=%s 
                WHERE id=%s
            ''', (_nombre, _descripcion, fecha_actual, _id))
    
    conexion.commit()
    cursor.close()
    
    flash('Producto actualizado exitosamente', 'success')
    return redirect('/admin/Productos')
    
@app.route('/admin/categoria/borrar', methods =['POST'])
def admin_categria_delete():
    _id = request.form['txtID']
    

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias WHERE id = %s",(_id,))
    categoria = cursor.fetchall()
    conexion.commit()
    print(categoria)

    
    
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("DELETE FROM categorias WHERE id=%s",(_id,))
    conexion.commit()

    return redirect('/admin/Productos')


@app.route('/cliente/Catalogo')
def cliente_catalogo():
    lista_productos = []
      
    try:
          cursor = conexion.cursor(dictionary=True)
          cursor.execute('SELECT * FROM productos')
          lista_productos = cursor.fetchall()
          print(lista_productos)
          conexion.commit()
          print('Conexion exitosa: ', conexion.is_connected())
         
          
    except mysql.connector.Error as err:
          flash(f'Error al conectar base de datos {err}')
          
          
    return render_template('/cliente/Catalogo.html', productos = lista_productos)


@app.route('/cliente/perfil')
def cliente_perfil():
    usuario = []
      
    try:
        # Obtener el id del usuario logueado de la sesión
        usuario_id = session.get('id')
        
        if not usuario_id:
            flash('No has iniciado sesión', 'danger')
            return redirect('/sitio/login')
        
        cursor = conexion.cursor(dictionary=True)
        
        # Ejecutar la consulta filtrando por el id del usuario
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (usuario_id,))
        
        usuario = cursor.fetchone()  # Obtenemos solo un usuario porque id es único
        print(usuario)
        
        # Conexion no necesita commit ya que es solo un SELECT
        print('Conexion exitosa: ', conexion.is_connected())
         
    except mysql.connector.Error as err:
        flash(f'Error al conectar base de datos {err}', 'danger')
          
    return render_template('/cliente/perfil.html', usuario = usuario)

@app.route('/cliente/logout')
def logout_cliente():
    
    
    session.pop('id', None)
    session.pop('id', None)
    session.pop('id', None)
    
    flash('Has cerrado correctamente tu sesion', 'success')
    
    return redirect('/sitio/login')


@app.route('/cliente/Pedidos')
def pedidos_clientes():
    
    pedidos = []
    
    try:
        
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
        SELECT 
            pedidos.id AS pedido_id, 
            pedidos.total, 
            pedidos.metodo_pago, 
            pedidos.estado, 
            pedidos.direccion_envio, 
            pedidos.fecha_pedido, 
            usuarios.nombre AS usuario_nombre
        FROM pedidos
        JOIN usuarios ON pedidos.usuario_id = usuarios.id
""")
        pedidos = cursor.fetchall()
        
        
        
        
    except mysql.connector.Error as err:
        print('Error al conectar BD: {err}') 
    
    finally:
        
        cursor.close()   
        
    
    return render_template('/cliente/Pedidos.html', pedidos = pedidos)   
    
@app.route('/cliente/Pedidos/cancelado', methods = ['POST'])
def pedido_cancelar():
    pedido_id = request.form.get('id')
    
    
    if not pedido_id: 
        
        return 'Error, falta ID del pedido', 400
    
    try:
        
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM pedidos WHERE id = %s', (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido: 
            
            return 'Pedido con ID: {pedido_id} no fue encontrado', 404
        
        cursor.execute('UPDATE pedidos SET estado = %s WHERE id = %s', ('cancelado', pedido_id))
        conexion.commit()
        
    except mysql.connector.Error as err:
        
        print('Error al conectar BD: {err}')   
        
    finally:
        cursor.close()
        
    return redirect('/cliente/Pedidos') 
    
   

@app.route('/carrito/agregar', methods=['POST'])
def agregar_carrito():
    
    if 'id' not in session: 
        flash('Debes iniciar sesion para agregar productos al carrito de compras')
        return redirect('/sitio/login')
    
    producto_id = request.form['producto_id']
    cantidad = int(request.form['cantidad'])
    
    if not cantidad: 
        flash('La cantidad es requerida', 'danger')
        return redirect('/cliente/inicio_cliente')
    
    
    
    try:
        
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar el stock disponible
        cursor.execute('SELECT stock FROM productos WHERE id = %s', (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            flash('Producto no encontrado.', 'danger')
            return redirect('/cliente/inicio_cliente')

        stock_disponible = producto['stock']
        
        # Comparar la cantidad solicitada con el stock disponible
        if cantidad > stock_disponible:
            flash(f'No hay suficiente stock. Solo hay {stock_disponible} unidades disponibles.', 'danger')
            return redirect('/cliente/inicio_cliente')
       
        
        cursor.execute('SELECT * FROM carritos WHERE usuario_id = %s',( session['id'],))
        carrito = cursor.fetchone()
        
        if not carrito: 
            cursor.execute('INSERT INTO carritos (usuario_id, fecha_creacion) VALUES (%s, NOW())',
                           (session['id'],))
            conexion.commit()
            carrito_id = cursor.lastrowid
        
        else:
            carrito_id = carrito['id']
            
        
        cursor.execute('SELECT * FROM carrito_productos WHERE id = %s AND producto_id = %s',
                       (carrito_id, producto_id ))
        producto_en_carrito = cursor.fetchone()
        
        if producto_en_carrito:
            nueva_cantidad = producto_en_carrito['cantidad'] + cantidad 
            cursor.execute('UPDATE carrito_productos SET cantidad = %s WHERE id = %s',
                           (nueva_cantidad, producto_en_carrito['id'] ))
            
        else:
            cursor.execute('INSERT INTO carrito_productos (carrito_id, producto_id, cantidad) VALUES (%s,%s,%s)',
                           (carrito_id, producto_id, cantidad))
        
        
        conexion.commit()
        flash('Producto agregado al carrito', 'success')
    
    except mysql.connector.Error as err:
        flash(f'Error al agregar el producto al carrito: {err}', 'danger')
        
    finally:
        cursor.close()
        
    return redirect('/cliente/inicio_cliente')

@app.route('/carrito/show')
def show_carrito():
    
    if 'id' not in session: 
        flash('Debes de iniciar sesion para ver tu carrito', 'warning')
        return redirect('/sitio/login')
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('''
                       
                       SELECT cp.id AS carrito_productos_id, p.nombre, p.precio, cp.cantidad, (p.precio * cp.cantidad) AS total
                       FROM carrito_productos cp 
                       JOIN productos p ON cp.producto_id = p.id 
                       JOIN carritos c ON cp.carrito_id = c.id 
                       WHERE c.usuario_id = %s
                       ''', (session['id'],))
        productos = cursor.fetchall()
    
    except mysql.connector.Error as err:
        flash(f'Error al cargar el carrito: {err}', 'danger')
        productos = []
    
    finally:
        cursor.close()
    
    return render_template('/cliente/ver_carrito.html', productos = productos)

@app.route('/carrito/eliminar_producto', methods=['POST'])
def delete_carrito():
    
    _id_product = request.form.get('producto_id')
    eliminar_todo = request.form.get('eliminar_todo')
    cantidad = request.form.get('cantidad')
    
    
    cursor = conexion.cursor(dictionary=True)
    user_id = session.get('id')  
    cursor.execute('SELECT id FROM carritos WHERE usuario_id = %s', (user_id,))
    carrito = cursor.fetchone()
    id_carrito = carrito['id'] if carrito else None
    
    if eliminar_todo == 'true':
        cursor.execute('DELETE FROM carrito_productos WHERE carrito_id=%s', (id_carrito,))
        flash('El carrito ha sido vaciado', 'success')
    
    elif cantidad:
        cantidad = int(cantidad)
        cursor.execute('''
                       
                       SELECT cantidad FROM carrito_productos WHERE id = %s
                       
                       ''', (_id_product,))
        
        resultado = cursor.fetchone()
        
        if resultado and resultado['cantidad'] > cantidad: 
            nueva_cantidad = resultado['cantidad'] - cantidad
            cursor.execute('''
                        
                        UPDATE carrito_productos SET cantidad = %s WHERE id = %s
                        
                        ''', (nueva_cantidad, _id_product))
            flash(f"Se eliminaron {cantidad} unidades del producto.", "success")
        else:
            cursor.execute(
                    "DELETE FROM carrito_productos WHERE id = %s",
                    (_id_product,)
                )
            flash("El producto fue eliminado del carrito.", "success")

    else:  
        cursor.execute(
            "DELETE FROM carrito_productos WHERE id = %s",
            (_id_product,)
        )
        flash("El producto fue eliminado completamente del carrito.", "success")
    
    conexion.commit()
    cursor.close()
    return redirect('/carrito/show')
    
    
@app.route('/carrito/finalizar_compra', methods=['GET','POST'])
def finalizar_compra():
    
    try:
          
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM carritos WHERE usuario_id = %s', (session['id'],))
        carrito = cursor.fetchone()
        
        if not carrito:
            flash('No tienes productos en tu carrito', 'info')
            return redirect('/cliente/catalogo')
        
        carrito_id = carrito['id']
        
        cursor.execute('''
                       
                       SELECT SUM(cp.cantidad * p.precio) AS total
                       FROM carrito_productos cp
                       JOIN productos p ON cp.producto_id = p.id
                       WHERE cp.carrito_id = %s
                       
                       ''', (carrito_id,))
        
        total_resultado = cursor.fetchone()
        total = total_resultado['total'] if total_resultado and total_resultado['total'] else 0
        
        if total == 0:
            flash('El carrito esta vacio o no tiene productos validos', 'info')
            return redirect('/cliente/inicio_cliente')
        
        return render_template('/cliente/finalizar_compra.html', total=total, carrito_id=carrito_id)
    
    except mysql.connector.Error as err:
        flash('Error al procesar la compra', err)
          

@app.route('/carrito/pagar', methods=['POST', 'GET'])
def pagar():
    
    if request.method == 'POST':
        carrito_id = request.form.get('carrito_id')
        total = float(request.form.get('total', 0))
        metodo_pago = request.form.get('metodo_pago')
        direccion_envio = request.form.get('direccion_envio')

      
        if not carrito_id or not metodo_pago or not direccion_envio:
            flash('Todos los campos son obligatorios. Por favor, complete la información.', 'warning')
            return redirect('/carrito/finalizar_compra')  

        try:
            cursor = conexion.cursor()
            estado = 'pendiente'

            cursor.execute(''' 
                INSERT INTO pedidos(usuario_id, total, metodo_pago, estado, direccion_envio, fecha_pedido) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            ''', (session['id'], total, metodo_pago, estado, direccion_envio))

            pedido_id = cursor.lastrowid

            cursor.execute(''' 
                INSERT INTO pedido_detalles (pedido_id, producto_id, cantidad, precio_unitario) 
                SELECT %s, producto_id, cantidad, p.precio 
                FROM carrito_productos cp 
                JOIN productos p ON cp.producto_id = p.id 
                WHERE cp.carrito_id = %s
            ''', (pedido_id, carrito_id))
            
            print(f"Actualizando stock para carrito_id: {carrito_id}")
            cursor.execute(''' 
                UPDATE productos p 
                JOIN carrito_productos cp ON p.id = cp.producto_id 
                SET p.stock = p.stock - cp.cantidad 
                WHERE cp.carrito_id = %s
            ''', (carrito_id,))
            cursor.execute('DELETE FROM carrito_productos WHERE carrito_id = %s', (carrito_id,))

            conexion.commit()

            flash('Compra completada exitosamente.', 'success')
            return redirect('/cliente/inicio_cliente')

        except mysql.connector.Error as err:
            print(f'Error al completar la compra: {err}')
            conexion.rollback()
            return redirect('/carrito/finalizar_compra') 

        finally:
            cursor.close()

   
    return redirect('/cliente/inicio_cliente')



@app.route('/api/catalogo', methods=['GET'])
def obtener_catalogo():
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Productos')
        lista_productos = cursor.fetchall()
        conexion.commit()
        
        
        return jsonify(lista_productos)
        
    except mysql.connector.Error as err:
        return jsonify({'error': f'Error de conexión: {err}'}), 500  





if __name__ =='__main__':
    app.run(debug=True)
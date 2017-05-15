from bottle import Bottle, route, run, template, get, post, request
import pymysql
import os
import datetime
import python_jwt as jwt
import Crypto.PublicKey.RSA as RSA
app = Bottle()

mysql_config = {
    'host': 'localhost',
    'db': 'spt',
    'user': 'root',
    'passwd': 'coke'
}

usuarios = {}
usuarios['junior'] = "123"
usuarios['andi'] = "456"

#clave privada, para crear token
private_key_file = os.path.join(os.path.dirname(__file__), 'keys','svc-key')
with open(private_key_file, 'r') as fd:
    private_key = RSA.importKey(fd.read())

#clave publica para verificar token
public_key_file = os.path.join(os.path.dirname(__file__), 'keys', 'svc-key.pub')
with open(public_key_file, 'r') as fd:
    public_key = RSA.importKey(fd.read())


def mysqlConfig():

    try:
        cnx = pymysql.connect(**mysql_config)
        cursor = cnx.cursor()
        insert_test = "INSERT INTO test (id, msg) VALUES (%s, %s)"
        data = ("200", "test message") # tupla
        cursor.execute(insert_test, data)

        cnx.commit()
        cursor.close()
    except pymysql.Error as err:
        print "Failed to insert data: {}".format(err)
    finally:
        if cnx:
            cnx.close()



@app.route('/hello', method="GET")
def hello():
    return "Hello World!"

@app.get('/')
@app.get('/hello/<name>')
def greet(name='Stranger'):
    return template('Hello {{name2}}', name2=name)

#funcion que testea si se recibio token
@app.get('/test')
def test():
    data = request.headers['Authorization']
    print "funcion test \n header:"
    print data
    ret = {"status": "OK", "token": data}
    return ret

#valida usuario y password en la base de datos
@app.post('/login')
def login():

    data = request.json
    usr = data['usuario']
    psw = data['password']

    u = usuarios.get(usr)
    print("recibi:")
    print("usuario:" + usr)
    print("password:" + psw + "\n\n")


    # deberia hacer la conexion a la bd una sola vez o por cada consulta ?
    try:
        cnx = pymysql.connect(**mysql_config)
        cursor = cnx.cursor()
        query = "SELECT `username`,`password` FROM `usuarios` WHERE `username`= %s"
        cursor.execute(query, usr)
        result = cursor.fetchone()
        print("result:")
        print(result)
        if(not result):
            print ("usuario no existe en base de datos")
            ret = {"status": "FAIL", "msg": "usuario y/o password invalido"}
            return ret
        else:
            print ("usuario existe => comprobar password")
            if(result[1] == psw):
                print ("logueado correcto")

                payload = {'username': usr, 'role': 'admin'};
                token = jwt.generate_jwt(payload, private_key, 'RS256', datetime.timedelta(minutes=5))
                ret = {"status": "OK",
                       "msg": "logueado correcto",
                       "token":token
                       }

                return ret
            else:
                print ("password estaba mal")
                ret = {"status": "FAIL", "msg": "usuario y/o password invalido"}
                return ret
        cnx.commit()
        cursor.close()
    except pymysql.Error as err:
        print "Failed to insert data: {}".format(err)
    finally:
        if cnx:
            cnx.close()

#valida registro en base de datos, controlando no existe otro usuario identico
@app.post('/register')
def register():

    print('entro a register')
    data = request.json
    usr = data['usuario']
    psw = data['password']
    psw2 = data['password2']

    u = usuarios.get(usr)

    try:
        cnx = pymysql.connect(**mysql_config)
        cursor = cnx.cursor()
        query = "SELECT `username`,`password` FROM `usuarios` WHERE `username`= %s"
        cursor.execute(query, usr)
        result = cursor.fetchone()
        print("result:")
        print(result)

        if(not result):
            print ("usuario no existe en base de datos => puedo crearlo")
            if(psw == psw2):
                print ("passwords que ingreso eran iguales => creo usuario en bd")
                insert = "INSERT INTO usuarios (username, password) VALUES (%s, %s)"
                usuario = (usr, psw)
                cursor.execute(insert, usuario)
                cnx.commit()
                cursor.close()

                payload = {'username': usr, 'role': 'admin'};
                token = jwt.generate_jwt(payload, private_key, 'RS256', datetime.timedelta(minutes=5))
                ret = {"status": "OK",
                       "msg": "usuario creado correctamente",
                       "token": token
                       }
                return ret
            else:
                cnx.commit()
                cursor.close()
                ret = {"status": "FAIL", "msg": "passwords no eran iguales"}
                return ret

        else:
            print ("usuario existe en la base de datos")
            cnx.commit()
            cursor.close()
            ret = {"status": "FAIL", "msg": "usuario ya existe."}
            return ret
        cnx.commit()
        cursor.close()
    except pymysql.Error as err:
        print "Failed to insert data: {}".format(err)
    finally:
        if cnx:
            cnx.close()



if __name__ == '__main__':
    mysqlConfig()

run(app, host='127.0.0.1', port=8081)

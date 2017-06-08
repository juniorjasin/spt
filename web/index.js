var express = require('express');
var session = require('express-session');
var handlers = require('express-handlebars').create({ defaultLayout: 'main' }); // busca siempre en views/layout el archivo main.handlebars
var bodyParser = require('body-parser');
var request = require('request');
var app = express();

app.engine('handlebars', handlers.engine);
app.set('view engine', 'handlebars');

app.use(bodyParser.urlencoded({extended:false}));

// inicializamos el modulo de session
app.use(session({
  secret: 'mys3cr3t',
  resave: false,
  saveUninitialized: true,
  cookie:{secure:false}
}));

// punto de entrada a la app. verifica si la session esta activa
// y te redirige segun corresponda
app.get('/', function (req, res) {
    var sess = req.session
    if(sess.token){
        res.redirect("/dashboard")
    }else{
        res.redirect("/login")
    }
});

// ruta test para verificar si llega token
app.get('/test', function (req, res) {

    var sess = req.session
    if(!sess.token){
        res.redirect("/login")
    }else{

        var options = {
            method: 'GET',
            uri: 'http://auth-svc:8081/test', // autenticacion (api ptyhon)
            headers: {
              'Authorization':'Bearer ' +sess.token,
              'content-type': 'application/json'
          },
          json:{}
          };

          request(options, function (error, response, body) {
             if(!error && response.statusCode == 200){
               console.log(body.status);
               if(body.status == "OK"){
                 // aca tenemos que crear el token // funciona
                 sess.token = body.token; // guardamos lo que el servicio de auth nos da como token
                 console.log("token recibido:\n");
                 console.log(sess.token);
                 res.redirect("/dashboard");
               } else {
                  res.render('login', {status:body.msg});
               }
             }
          });
        }
});

// vista principal, cuando ya se encuentra loggueado
app.get('/dashboard', function (req, res) {
    res.render('dashboard');
});

// vista del log in
app.get('/login', function (req, res) {
    var sess = req.session
    if(sess.token){
        res.redirect("/dashboard")
    }else{
        res.render('login');
    }
});

// se llama cuando se ingresan los datos en el login // le puedo llamar login tambien porque este es post y NO get
app.post('/verify_user', function (req, res) {
  var nom = req.body.nombre;
  var pass = req.body.pass;
  var sess = req.session
  var status;
  if(nom == '' || pass == ''){
    status = 'datos Incorrectos';
    res.render('home', {status:"debe completar los campos..."});
  }else{

    // le hago un post a mi servicio para que controle los datos
      var options = {
          method: 'POST',
          uri: 'http://auth-svc:8081/login', // autenticacion (api ptyhon)
          headers: {
            'content-type': 'application/json'
          },
          json: {
            "usuario": nom,
            "password": pass
          }
        };

        console.log("envio:");
        console.log("usuario:" + nom);
        console.log("password:" + pass + "\n\n");

        request(options, function (error, response, body) {
           if(!error && response.statusCode == 200){
             console.log(body.status);
             if(body.status == "OK"){

               // aca tenemos que crear el token // funciona
               sess.token = body.token; // guardamos lo que el servicio de auth nos da como token
               console.log("token recibido:\n");
               console.log(sess.token);
               res.redirect("/dashboard");

             } else {
                res.render('login', {status:body.msg});
             }
           }
        });
      }
});

// cuando desde /home se presiona el button Sing In. muestra el formulario para registrarse
app.get('/register', function (req, res) {
    res.render('register');
});

// aca se procesan los datos de la vista register
app.post('/create_user', function (req, res) {
  var user = req.body.username;
  var pass = req.body.pass;
  var pass2 = req.body.pass2;
  var sess = req.session

  if(user == '' || pass == '' || pass2 == ''){
    res.render('register', {status:"debe completar todos los campos..."})
  }else if(pass == pass2){

      // hace falta mandar las dos contraseñas si ya se que son iguales ?
      // le hago un post a mi servicio para que controle los datos
        var options = {
            method: 'POST',
            uri: 'http://auth-svc:8081/register', // autenticacion (api ptyhon)
            headers: {
              'content-type': 'application/json'
            },
            json: {
              "usuario": user,
              "password": pass,
              "password2":pass2
            }
          };

          request(options, function (error, response, body) {
             if(!error && response.statusCode == 200){
               console.log(body.status);
               if(body.status == "OK"){

                   sess.token = body.token; // guardamos lo que el servicio de auth nos da como token
                   console.log("token recibido:\n");
                   console.log(sess.token);
                   res.redirect("/dashboard");
               } else {
                  res.render('register', {status:body.msg});
               }
             }
          });

  }else{
    res.render('register', {status:"las contraseñas no coinciden..."})
  }
});


app.listen(3000);

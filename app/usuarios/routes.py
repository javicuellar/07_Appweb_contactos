from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user

from app.app import app, db, login_manager
from .models import Usuarios
from .forms import LoginForm, formUsuario





@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))



@app.route('/', methods=['get', 'post'])
@app.route('/login', methods=['get', 'post'])
def login():
	# Control de permisos
	if current_user.is_authenticated:
		return redirect(url_for("contactos"))

	form = LoginForm()
	if form.validate_on_submit():
		user=Usuarios.query.filter_by(username=form.username.data).first()
		if user!=None and user.verify_password(form.password.data):
			login_user(user)
			next = request.args.get('next')
			return redirect(next or url_for('contactos'))
		form.username.errors.append("Usuario o contraseña incorrectas.")
	return render_template('usuarios/login.html', form=form)



@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))



@app.route("/registro",methods=["get","post"])
def registro():
	# Control de permisos
	if current_user.is_authenticated:
		return redirect(url_for("contactos"))

	form=formUsuario()
	if form.validate_on_submit():
		existe_usuario=Usuarios.query.filter_by(username=form.username.data).first()
		if existe_usuario==None:
			user=Usuarios()
			form.populate_obj(user)
			user.admin=False
			db.session.add(user)
			db.session.commit()
			return redirect(url_for("contactos"))
		form.username.errors.append("Nombre de usuario ya existe.")
	return render_template("usuarios/registro.html",form=form)

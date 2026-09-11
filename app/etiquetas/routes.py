from flask import render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from app.app import app, db
from .models import Etiquetas
from .forms import formEtiqueta, formSINO






@app.route('/etiquetas/')
@login_required
def etiquetas(id='0'):
	etiquetas = Etiquetas.query.all()
	
	return render_template("etiquetas/etiquetas.html", etiquetas=etiquetas)



@app.route('/etiqueta/new', methods=["get","post"])
@app.route('/etiqueta/<id>/edit', methods=["get","post"])
@login_required
def etiqueta_edit(id=None):
	# Control de permisos
	if not current_user.is_admin():
		abort(404)

	if id is None:
		form= formEtiqueta()
		eti = Etiquetas()
	else:
		eti = Etiquetas.query.get(id)
		if eti is None:
			abort(404)

		form= formEtiqueta(obj=eti)
	
	if form.validate_on_submit():
		form.populate_obj(eti)

		if id is None:
			db.session.add(eti)
		db.session.commit()
		
		return redirect(url_for("etiquetas"))
	
	return render_template("etiquetas/etiqueta_new.html",form=form, id=id)



@app.route('/etiqueta/<id>/delete', methods=["get","post"])
@login_required
def etiqueta_delete(id):
	# Control de permisos
	if not current_user.is_admin():
		abort(404)

	eti = Etiquetas.query.get(id)
	if eti is None:
		abort(404)

	form = formSINO()
	if form.validate_on_submit():
		if form.si.data:
			db.session.delete(eti)
			db.session.commit()
		return redirect(url_for("etiquetas"))
	return render_template("etiquetas/etiqueta_delete.html", form=form, eti=eti)

from flask import render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user

from app.app import app, db
from .models import Contactos, Rel_contacto_etiqueta
from .forms import formContacto, formSINO
from app.etiquetas.models import Etiquetas

from app.comunes.utilidades import procesar_archivo




@app.route('/contactos/')
@app.route('/contactos/<id>')
@login_required
def contactos(id='0'):
	etiqueta = Etiquetas.query.get(id)
	etiquetas = Etiquetas.query.order_by(Etiquetas.nombre.asc()).all()
	
	#  busqueda de contactos por nombre "parecido"
	#  Contacto.query.filter(Contacto.nombre.ilike(f'%{busqueda}%')).all()

	if id == '0':
		contactos = Contactos.query.all()
	else:
		rel = Rel_contacto_etiqueta.query.filter_by(EtiquetaId=id).all()
		lista_ids = [c.ContactoId for c in rel]
		contactos = Contactos.query.filter(Contactos.id.in_(lista_ids)).all()
	return render_template("contactos/contactos.html",contactos=contactos, etiquetas=etiquetas, etiqueta=etiqueta)



@app.route('/contactos/new', methods=["get","post"])
@login_required
def contactos_new(etiquetas=[]):
	# Control de permisos
	if not current_user.is_admin():
		abort(404)

	form = formContacto()
	form.Etiquetas.choices = [('0', 'Ninguna')] + [(str(c.id), c.nombre) for c in Etiquetas.query.all()[1:]]

	if form.validate_on_submit():
		cont = Contactos()
		form.populate_obj(cont)
		db.session.add(cont)
		db.session.commit()
		
		# Añadimos las nuevas etiquetas seleccionadas
		for etiqueta in [int(c) for c in form.Etiquetas.data]:
			if etiqueta == 0:
				continue

			rel = Rel_contacto_etiqueta()
			rel.ContactoId = cont.id
			rel.EtiquetaId = etiqueta
			db.session.add(rel)
			db.session.commit()
		return redirect(url_for("contactos"))
	
	return render_template("contactos/contactos_new.html",form=form, etiquetas=etiquetas)



@app.route('/contactos/<id>/edit', methods=["get","post"])
@login_required
def contactos_edit(id):
	# Control de permisos
	if not current_user.is_admin():
		abort(404)

	cont = Contactos.query.get(id)
	if cont is None:
		abort(404)

	form= formContacto(obj=cont)
	form.Etiquetas.choices = [('0', 'Ninguna')] + [(str(c.id), c.nombre) for c in Etiquetas.query.all()[1:]]
	
	if form.validate_on_submit():
		form.populate_obj(cont)
		
		# Borramos las etiquetas anteriores
		rel = Rel_contacto_etiqueta.query.filter_by(ContactoId=id).all()
		for etiqueta in rel:
			db.session.delete(etiqueta)
		
		# Añadimos las nuevas etiquetas seleccionadas
		for etiqueta in [int(c) for c in form.Etiquetas.data]:
			if etiqueta == 0:
				continue

			rel = Rel_contacto_etiqueta()
			rel.ContactoId = cont.id
			rel.EtiquetaId = etiqueta
			db.session.add(rel)
		
		db.session.commit()
		return redirect(url_for("contactos"))

	# Obtener los Ids de las etiquetas asociadas al contacto para marcarlas
	form.Etiquetas.data = [str(c.EtiquetaId) for c in Rel_contacto_etiqueta.query.filter_by(ContactoId=id).all()]
	# si no hay etiquetas asociadas, se marca la primera por defecto "Ninguna"
	if form.Etiquetas.data == []:
		form.Etiquetas.data = ['0']
	
	return render_template("contactos/contactos_new.html",form=form, id=id)



@app.route('/contactos/<id>/delete', methods=["get","post"])
@login_required
def contactos_delete(id):
		# Control de permisos
	if not current_user.is_admin():
		abort(404)

	cont = Contactos.query.get(id)
	if cont is None:
		abort(404)

	form = formSINO()
	if form.validate_on_submit():
		if form.si.data:
			db.session.delete(cont)
			db.session.commit()
		return redirect(url_for("contactos"))
	return render_template("contactos/contactos_delete.html",form=form,cont=cont)



@app.route('/subir', methods=['POST'])
def subir_archivo():
	if 'archivo' not in request.files:
		print('No se ha seleccionado ningún archivo.')
    
	archivo = request.files['archivo']
    
	if archivo.filename == '':
		print('No se ha seleccionado ningún archivo.')
    
	contactos = procesar_archivo(archivo)

	# Procesar y guardar los contactos en la base de datos
	for contacto in contactos:
		cont_bd = Contactos.query.filter(Contactos.nombre == contacto['nombre']).all()
		if len(cont_bd) == 0:
			cont = Contactos()
			cont.nombre = contacto['nombre']
			cont.apellidos = ''
			if 'notas' in contacto:
				cont.notas = contacto['notas']
			else:
				cont.notas = ''
		
			db.session.add(cont)
			db.session.commit()
			
			# Tratamiento de las etiquetas, si las hay
			if 'etiquetas' in contacto:
				for etiqueta in contacto['etiquetas']:
					eti = Etiquetas.query.filter(Etiquetas.nombre==etiqueta).first()
					if eti is None:
						# print(f"  > Etiquetas: Añadiendo etiqueta {etiqueta}")
						eti = Etiquetas()
						eti.nombre = etiqueta
						eti.descripcion = ''
						db.session.add(eti)
						db.session.commit()
					
					rel = Rel_contacto_etiqueta()
					rel.ContactoId = cont.id
					rel.EtiquetaId = eti.id
					db.session.add(rel)
					db.session.commit()

		else:
			print(f"El contacto {contacto['nombre']} ya existe en la base de datos. Hay {len(cont_bd)} coincidencias.")
			print(f"  > Datos del contacto - {contacto}")

		db.session.commit()
    
	print('Archivo procesado exitosamente.')
	return redirect(url_for("contactos"))

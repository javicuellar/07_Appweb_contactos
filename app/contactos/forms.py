from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired






class formContacto(FlaskForm):                      
	nombre 		= StringField("Nombre:", validators=[DataRequired("Tienes que introducir el dato")])
	apellidos 	= StringField("Apellidos:", validators=[DataRequired("Tienes que introducir el dato")])
	notas 		= TextAreaField("Notas:")
	Etiquetas 	= SelectMultipleField("Etiqueta:", validators=[DataRequired()])
	submit 		= SubmitField('Enviar')



class formEtiqueta(FlaskForm):                      
	nombre = StringField("Etiqueta:", validators=[DataRequired("Tienes que introducir el dato")])
	submit = SubmitField('Enviar')



class formSINO(FlaskForm):      
	si = SubmitField('Si') 
	no = SubmitField('No') 

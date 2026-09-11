from sqlalchemy import Column , ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from app.app import db






class Contactos(db.Model):
	"""Contactos"""
	__tablename__ = 'contactos'
	id = Column(Integer, primary_key=True)
	nombre = Column(String(100),nullable=False)
	apellidos = Column(String(100),nullable=True)
	notas = Column(String(255))
	rel_etiquetas = relationship("Rel_contacto_etiqueta", cascade="all, delete-orphan", lazy='dynamic')

	def __repr__(self):
		return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))



class Rel_contacto_etiqueta(db.Model):
	"""Relación entre contactos y etiquetas"""
	__tablename__ = 'rel_contacto_etiqueta'
	id 			= Column(Integer, primary_key=True)
	EtiquetaId 	= Column(Integer, ForeignKey('etiquetas.id'), nullable=False)
	ContactoId 	= Column(Integer, ForeignKey('contactos.id'), nullable=False)

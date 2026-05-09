from __future__ import annotations

from django.db import models
from django.utils import timezone


class Autor(models.Model):
    """
    Representa a un autor/a.
    Requerido: nombre, email único, biografía opcional.
    """
    # nombre   → CharField (max_length a elección)
    nombre =models.CharField(max_length=120)
    # email    → EmailField (unique=True)
    email = models.EmailField(unique = True)
    # biografia → TextField (blank=True para hacerlo opcional)
    biografia = models.TextField(blank=True, null=True)
    pass

    # Opcional: definir __str__ para que sea legible en el admin y en el shell
    def __str__(self) -> str:
        return self.nombre

class Categoria(models.Model):
    """
    Categoría temática de libros.
    Ejemplos: 'fantasía', 'ciencia ficción', 'historia'.
    """
    # Campo nombre: único para evitar categorías duplicadas
    nombre = models.CharField(max_length=100, unique=True)
    pass

    def __str__(self) -> str:
        """Retorna el nombre de la categoría para mostrar en admin y shell."""
        return self.nombre


class Libro(models.Model):
    """
    Libro del catálogo de la biblioteca.
    Tiene relación N:1 con Autor y N:M con Categoria.
    """
    # Campo título: nombre del libro
    titulo = models.CharField(max_length=200)

    # Campo ISBN: código único internacional del libro, nunca se repite
    isbn = models.CharField(max_length=13, unique=True)

    # Campo fecha de publicación
    fecha_publicacion = models.DateField()

    # Campo cantidad total: número de copias disponibles, solamente números positivos
    cantidad_total = models.PositiveIntegerField()

    # Relación N:1 con Autor (un libro tiene un autor), on_delete=models.PROTECT para evitar borrar un autor si tiene libros relacionados.
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name='libros')

    # Relación N:M con Categoria (un libro puede tener múltiples categorías) "related_name" permite acceder a los libros desde la categoría
    categorias = models.ManyToManyField(Categoria, related_name='libros')
    pass

    def __str__(self) -> str:
        """Retorna título y autor para identificación del libro."""
        return f"{self.titulo} - {self.autor.nombre}"

    def prestamos_activos(self) -> int:
        """
        Retorna la cantidad de préstamos activos (fecha_devolucion IS NULL).
        Un préstamo es "activo" cuando no se ha registrado devolución.
        """
        # self.prestamo_set es el administrador relacionado que Django crea automáticamente para la relación inversa desde Prestamo hacia Libro, es equivalente a Prestamo.objects.filter(libro=self), .count() devuelve la cantidad de objetos en el QuerySet resultante.
        return self.prestamo_set.filter(fecha_devolucion__isnull=True).count()

    def disponibles(self) -> int:
        """
        Retorna cuántas copias están disponibles:
        cantidad_total - prestamos_activos()
        """
        # Llamamos al método prestamos_activos() definido en este mismo modelo.
        # Ese método ya usa ORM para contar préstamos sin fecha de devolución.
        prestamos_activos = self.prestamos_activos()
        return self.cantidad_total - prestamos_activos

    def tiene_disponibles(self) -> bool:
        """Retorna True si hay al menos una copia disponible."""
        # Reutilizamos el método disponibles() que ya usa ORM para calcular
        # la cantidad de copias disponibles (cantidad_total - prestamos_activos)
        # Si el resultado es mayor que 0, significa que hay copias disponibles
        return self.disponibles() > 0


class Prestamo(models.Model):
    """
    Registro de un préstamo de libro a un usuario.
    Si fecha_devolucion es NULL → el préstamo está activo.
    """
    # Relación con Libro: un préstamo pertenece a un libro
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE,related_name='prestamo_set')
    # Nombre de la persona que toma prestado el libro
    nombre_prestatario = models.CharField(max_length=200)
    # Fecha en que se realizó el préstamo
    fecha_prestamo = models.DateField()
    # Fecha de devolución (NULL si el préstamo está activo)
    fecha_devolucion = models.DateField(null=True, blank=True)
    pass

    def __str__(self) -> str:
        """Retorna información del préstamo para identificación."""
        estado = "Activo" if self.fecha_devolucion is None else "Devuelto"
        return f"{self.libro.titulo} - {self.nombre_prestatario} ({estado})"

from eventsourcing.domain import Aggregate, event
from eventsourcing.application import Application
import os

# Configuración del entorno de persistencia
os.environ["PERSISTENCE_MODULE"] = 'eventsourcing.sqlite'
os.environ["SQLITE_DBNAME"] = 'instudio.db'

# Definimos la clase de agregados para las reservas en InStudio
class Reservation(Aggregate):
    @event('Created')
    def __init__(self, client_name, salon_id, service):
        self.client_name = client_name
        self.salon_id = salon_id
        self.service = service
        self.status = "Pending"
    
    @event('Canceled')
    def cancel(self):
        self.status = "Canceled"

    @event('Completed')
    def complete(self):
        self.status = "Completed"


# Aplicación principal para InStudio, gestionando las reservas
class InStudioApplication(Application):
    def create_reservation(self, client_name, salon_id, service):
        """Registra una nueva reserva y la guarda en el repositorio."""
        reservation = Reservation(client_name, salon_id, service)
        self.save(reservation)
        return reservation.id

    def cancel_reservation(self, reservation_id):
        """Cancela una reserva existente."""
        reservation = self.repository.get(reservation_id)
        reservation.cancel()
        self.save(reservation)

    def complete_reservation(self, reservation_id):
        """Marca una reserva como completada."""
        reservation = self.repository.get(reservation_id)
        reservation.complete()
        self.save(reservation)

    def get_reservation(self, reservation_id):
        """Recupera una reserva y su estado actual."""
        reservation = self.repository.get(reservation_id)
        return {
            'client_name': reservation.client_name,
            'salon_id': reservation.salon_id,
            'service': reservation.service,
            'status': reservation.status
        }


# Prueba del sistema de reservas en InStudio
def test_instudio_application():
    # Crear instancia de la aplicación
    instudio_app = InStudioApplication()

    # Registrar una nueva reserva
    reservation_id = instudio_app.create_reservation('Eduardo Ramón', 'salon_123', 'Corte de cabello')
    instudio_app.complete_reservation(reservation_id)

    # Obtener y verificar el estado de la reserva
    reservation = instudio_app.get_reservation(reservation_id)
    assert reservation['client_name'] == 'Eduardo Ramón'
    assert reservation['status'] == 'Completed'

    # Cancelar la reserva y verificar el estado
    instudio_app.cancel_reservation(reservation_id)
    reservation = instudio_app.get_reservation(reservation_id)
    assert reservation['status'] == 'Canceled'

    # Consultar notificaciones para ver los eventos generados
    notifications = instudio_app.notification_log.select(start=1, limit=10)
    assert len(notifications) == 3  # Creación, completado y cancelación

# Ejecutar la prueba
test_instudio_application()

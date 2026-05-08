from rest_framework.permissions import BasePermission
from empleados.models import Empleado


def get_user_empleado(user):
    if not user or not user.is_authenticated:
        return None

    # Si existe relación directa User -> Empleado
    empleado = getattr(user, 'empleado', None)
    if empleado:
        return empleado

    # Si el username coincide con el DNI del empleado
    if getattr(user, 'username', None):
        empleado = Empleado.objects.filter(dni=user.username).first()
        if empleado:
            return empleado

    return None


class EsEmpleadoActivo(BasePermission):
    message = 'Se requiere un empleado válido para acceder a esta API.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Permitir al admin/superusuario usar la API
        if request.user.is_staff or request.user.is_superuser:
            return True

        empleado = get_user_empleado(request.user)
        return bool(empleado)


class EsPropietarioOAdmin(BasePermission):
    message = 'Solo el empleado que creó la encomienda o un administrador puede modificarla.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        empleado = get_user_empleado(request.user)
        if not empleado:
            return False

        if hasattr(obj, 'empleado_registro'):
            return obj.empleado_registro == empleado

        return False
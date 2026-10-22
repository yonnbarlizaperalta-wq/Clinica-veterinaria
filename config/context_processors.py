def portal_roles(request):
    user = request.user
    if not user.is_authenticated:
        return {'portal_es_personal': False}
    return {
        'portal_es_personal': user.is_staff or user.is_superuser or user.groups.filter(name__in=['Recepcionista', 'Veterinario']).exists(),
    }

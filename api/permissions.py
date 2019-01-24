from rest_framework import permissions
from . import models
# SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
HARD_METHODS = ['POST', 'PATCH', 'PUT', 'DELETE']


class IsAdminLocal(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser:
            return True
        return False


class IsAdminUserLocal(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        print 'USER'
        print request.method
        print request.user.is_superuser
        if request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser:
            if request.method == 'DELETE':
                return obj.id != request.user.id
            else:
                return True
        return False


class IsPrincipalLocalOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.user and (request.user.is_principal or request.user.is_superuser):
            return True
        return False


class IsPrincipalOwnTechniqueLocal(permissions.BasePermission):

    def has_permission(self, request, view):
        # print 'has_permission'
        # print request.method

        if request.method in permissions.SAFE_METHODS or request.user and (request.user.is_principal or request.user.is_superuser):
            if request.method == 'POST' and request.user.is_principal:
                new_method = request.data.get('methodId')
                own_method = request.user.method.id
                return new_method == own_method
            else:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        # print 'has_object_permission'
        # print request.method
        if request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser:
            return True

        if request.method in HARD_METHODS and request.user.is_principal:
            new_method = obj.method.id
            own_method = request.user.method.id
            return new_method == own_method
        return False


class IsPrincipalOwnerLocal(permissions.BasePermission):

    def has_permission(self, request, view):
        # print 'has_permission'
        # print request.method
        if request.method in permissions.SAFE_METHODS or request.user and (request.user.is_principal or request.user.is_superuser):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # print 'has_object_permission'
        # print request.method

        if request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser:
            return True

        if request.method in HARD_METHODS and request.user.is_principal:

            if request.user.id == obj.owner.id:
                return True

        return False


class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        # print 'has_permission'
        # print request.method
        if request.method in permissions.SAFE_METHODS or request.user:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True

        return request.user.id == obj.owner.id


class IsPrincipalOwnerMethodByTechnique(permissions.BasePermission):

    def has_permission(self, request, view):
        print 'has_permission'
        print request.method
        print permissions.SAFE_METHODS
        if request.method in permissions.SAFE_METHODS and request.user:
            return True

        if request.user.is_principal or request.user.is_superuser:
            if request.method == 'POST' and request.user.is_principal:
                techniqueId = request.data.get('technique')
                technique = models.Technique.objects.filter(id=techniqueId)
                new_method = technique[0].method
                own_method = request.user.method.id
                if new_method.id == own_method:
                    return True
                else:
                    role = request.user.role
                    if role is not None:
                        roles = request.user.role.split(',')
                        return str(techniqueId) in roles
            else:
                return True
        else:
            if request.method == 'POST' and request.user:
                techniqueId = request.data.get('technique')
                role = request.user.role
                if role is not None:
                    roles = request.user.role.split(',')
                    return str(techniqueId) in roles
            else:
                return True
        # print 'SALIO'
        # return False

    def has_object_permission(self, request, view, obj):
        print 'has_object_permission'
        print request.method
        if request.method in permissions.SAFE_METHODS or request.user and request.user.is_superuser:
            return True

        if request.method in HARD_METHODS and request.user.is_principal:
            print 'has_object_permission'
            print obj
            print obj.technique.method.id
            new_method = obj.technique.method.id
            own_method = request.user.method.id
            role = request.user.role
            techniqueId = obj.technique.id
            if role is not None:
                roles = request.user.role.split(',')
                return (new_method == own_method or str(techniqueId) in roles) and request.user.id == obj.owner.id
            else:
                return new_method == own_method and request.user.id == obj.owner.id

        if request.method in HARD_METHODS and request.user:
            role = request.user.role
            techniqueId = obj.technique.id
            if role is not None:
                roles = request.user.role.split(',')
                return str(techniqueId) in roles and request.user.id == obj.owner.id

        return False


msg0 = 'No cuenta con permisos.'
msg1 = 'Debe ser propietarios del registro o de la plantilla para realizar modificaciones.'
msg2 = 'Debe ser propietarios del registro para realizar modificaciones.'
msg3 = 'No tiene permisos para registrar datos en la plantilla.'


class IsRowDefinitive(permissions.BasePermission):
    message = {'errors': [msg0]}

    def has_permission(self, request, view):
        # print 'has_object'
        print 'PERMISSIONS'
        print request.method
        self.message['errors'] = [msg0]
        if request.method in permissions.SAFE_METHODS or request.user:
            if request.method == 'POST':
                self.message['errors'] = [msg3]
                if request.user.is_superuser:
                    return True
                elif request.user.is_principal:
                    templateId = request.data.get('template')
                    template = models.Template.objects.get(pk=templateId)
                    method_template = template.technique.method
                    method_user = request.user.method
                    if method_template.id == method_user:
                        return True
                    else:
                        # return False
                        technique = template.technique
                        role = request.user.role
                        if role is not None:
                            roles = request.user.role.split(',')
                            return str(technique.id) in roles and template.state
                else:
                    templateId = request.data.get('template')
                    template = models.Template.objects.get(pk=templateId)
                    technique = template.technique
                    role = request.user.role
                    if role is not None:
                        roles = request.user.role.split(',')
                        return str(technique.id) in roles and template.state
            else:
                print 'tiene permisos 2'
                return True
        return False

    def has_object_permission(self, request, view, obj):
        print 'has_object_permission'
        print request.method
        self.message['errors'] = [msg0]
        if request.method in HARD_METHODS or request.user:
            if request.user.is_superuser:
                return True
            elif request.user.is_principal:
                self.message['errors'] = [msg1]
                print 'DELETE?'
                print request.user.id
                print obj.owner.id
                print obj.template.owner.id
                print '--------'
                return request.user.id in [obj.owner.id, obj.template.owner.id]
            else:
                self.message['errors'] = [msg2]
                return request.user.id == obj.owner.id
        return False


class IsUploadFile(permissions.BasePermission):
    message = {'errors': [msg0]}

    def has_permission(self, request, view):
        # print 'has_object'
        print 'PERMISSIONS'
        print request.method
        self.message['errors'] = [msg0]
        if request.method in permissions.SAFE_METHODS or request.user:
            if request.method == 'POST':
                self.message['errors'] = [msg3]
                if request.user.is_superuser:
                    return True
                elif request.user.is_principal:
                    templateId = request.data.get('template')
                    template = models.Template.objects.get(pk=templateId)
                    method_template = template.technique.method
                    method_user = request.user.method
                    if method_template.id == method_user:
                        return True
                    else:
                        # return False
                        technique = template.technique
                        role = request.user.role
                        if role is not None:
                            roles = request.user.role.split(',')
                            return str(technique.id) in roles and template.state
                else:
                    templateId = request.data.get('template')
                    template = models.Template.objects.get(pk=templateId)
                    technique = template.technique
                    role = request.user.role
                    if role is not None:
                        roles = request.user.role.split(',')
                        return str(technique.id) in roles and template.state
            else:
                print 'tiene permisos 2'
                return True
        return False

    def has_object_permission(self, request, view, obj):
        print 'has_object_permission'
        print request.method
        self.message['errors'] = [msg0]
        if request.method in HARD_METHODS or request.user:
            if request.user.is_superuser:
                return True
            elif request.user.is_principal:
                self.message['errors'] = [msg1]
                print 'DELETE?'
                print request.user.id
                print obj.owner.id
                print obj.template.owner.id
                print '--------'
                return request.user.id in [obj.owner.id, obj.template.owner.id]
            else:
                self.message['errors'] = [msg2]
                return request.user.id == obj.owner.id
        return False

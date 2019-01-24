from rest_framework import serializers, status
from rest_framework.response import Response
from . import models
from users.serializers import CustomUserSerializer
from users.models import CustomUser


# ############ HELPERS ################# #

class ParameterSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Parameter
        fields = ('id', 'label', 'unit', 'state')


class RowDefinitiveDataListSerializer(serializers.ModelSerializer):
    # parameter = ParameterSimpleSerializer(many=False, read_only=True)

    class Meta:
        model = models.RowDefinitiveData
        fields = ('value', 'parameter')

# ###################################### #


class VolcanoSerializer(serializers.ModelSerializer):

    # Example http://127.0.0.1:8000/api/v1/volcano/?fields=id,name,longitude&height=4501

    def __init__(self, *args, **kwargs):
        super(VolcanoSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.query_params.get('fields'):
            fields = request.query_params.get('fields')
            if fields:
                fields = fields.split(',')
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)

    class Meta:
        model = models.Volcano
        fields = '__all__'

    # def validate_height(self, value):
    #     if value < 2000:
    #         # return Response(self.errors, status=status.HTTP_400_BAD_REQUEST)
    #         raise serializers.ValidationError('La altura debe ser mayor a 2000 metros')
    #     return value


class MethodSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(MethodSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.query_params.get('fields'):
            fields = request.query_params.get('fields')
            if fields:
                fields = fields.split(',')
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)

    # principal = UserProfileSerializer(many=False, read_only=True)
    # principalId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=models.UserProfile.objects.all(), source='principal')
    # username = serializers.SlugRelatedField(source='principal.user', read_only=True, slug_field='username')
    # test = serializers.SerializerMethodField()

    class Meta:
        model = models.Method
        fields = ['id', 'name', 'description', 'color', 'icon', 'principal']

    # def get_test(self, obj):
    #     print 'GET TEST'
    #     print obj.principal.id
    #     qs = obj.principal
    #     return UserProfileSerializer(qs, many=False).data


class TechniqueSerializer(serializers.ModelSerializer):
    method = MethodSerializer(many=False, read_only=True)
    methodId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=models.Method.objects.all(), source='method')

    class Meta:
        model = models.Technique
        fields = ('id', 'name', 'description', 'method', 'methodId')


class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(many=False, read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=CustomUser.objects.all(), source='user')
    username = serializers.SlugRelatedField(source='user', read_only=True, slug_field='username')
    # method = serializers.BaseSerializer('api.MethodSerializer', many=False, read_only=True)
    # method = MethodSerializer(many=False, read_only=True)
    # method_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=models.Method.objects.all(), source='method')

    class Meta:
        model = models.UserProfile
        fields = ('id', 'description', 'username', 'user_id', 'user', 'created_at')

    # def validate_role(self, value):
    #     if value < 2000:
    #         # return Response(self.errors, status=status.HTTP_400_BAD_REQUEST)
    #         raise serializers.ValidationError('La altura debe ser mayor a 2000 metros')
    #     return value


class ParameterSerializer(serializers.ModelSerializer):
    owner_fn = serializers.SlugRelatedField(source='owner', read_only=True, slug_field='username')

    class Meta:
        model = models.Parameter
        fields = ('id', 'label', 'unit', 'owner', 'state', 'owner_fn')


class TemplateSerializer(serializers.ModelSerializer):
    records = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # parameters = ParameterSerializer(many=True, write_only=True)
    # parameters = serializers.ManyRelatedField(write_only=True)
    # state = serializers.IntegerField(max_value=1)
    volcano_name = serializers.SlugRelatedField(source='volcano', read_only=True, slug_field='name')
    technique_name = serializers.SlugRelatedField(source='technique', read_only=True, slug_field='name')
    method_id = serializers.SlugRelatedField(source='technique.method', read_only=True, slug_field='id')
    method_name = serializers.SlugRelatedField(source='technique.method', read_only=True, slug_field='name')
    owner_fn = serializers.SlugRelatedField(source='owner', read_only=True, slug_field='username')
    parameters_list = ParameterSimpleSerializer(many=True, read_only=True, source='parameters')

    class Meta:
        model = models.Template
        fields = ('id', 'label', 'technique', 'technique_name', 'method_id', 'method_name', 'volcano', 'volcano_name', 'owner', 'owner_fn', 'parameters',
                  'parameters_order', 'parameters_list', 'state', 'records')
        # extra_kwargs = {'parameters': {'write_only': True}}

    def validate(self, data):
        # user = self.context['request'].user
        print '-- --- --- --VALIDATE'
        new_technique = data.get('technique').id
        new_volcano = data.get('volcano').id
        if self.instance is not None:
            template = self.instance.id
            technique = self.instance.technique.id
            volcano = self.instance.volcano.id
            if models.RowDefinitive.objects.filter(template=template).count() > 0:
                print 'tiene dato'
                if technique == new_technique and volcano == new_volcano:
                    return data
                else:
                    raise serializers.ValidationError('No puede modificar la "Tecnica" o "Volcan", en una plantilla con registros.')
        return data


class RowDefinitiveSerializer(serializers.ModelSerializer):
    data = RowDefinitiveDataListSerializer(many=True, read_only=True)
    template_order = serializers.SlugRelatedField(source='template', read_only=True, slug_field='parameters_order')

    class Meta:
        model = models.RowDefinitive
        fields = ('id', 'description', 'date', 'template', 'template_order', 'volcano', 'owner', 'state', 'created_at', 'is_single_insert', 'data')


class RowDefinitiveDataSerializer(serializers.ModelSerializer):
    template = serializers.SlugRelatedField(source='row_definitive.template', read_only=True, slug_field='id')

    class Meta:
        model = models.RowDefinitiveData
        fields = ('id', 'value', 'parameter', 'row_definitive', 'template')



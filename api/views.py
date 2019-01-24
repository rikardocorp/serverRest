# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q, Count
from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from . import models
from . import serializers
from . import permissions
import datetime, json
from django.http import Http404
from rest_framework.permissions import AllowAny
from pagination import DefaultPagination
# Create your views here.


class VolcanoViewSet(viewsets.ModelViewSet):
    queryset = models.Volcano.objects.all()
    serializer_class = serializers.VolcanoSerializer
    permission_classes = [permissions.IsAdminLocal]

    # Example http://127.0.0.1:8000/api/v1/volcano/?height=4501

    def get_queryset(self):
        """ allow rest api to filter by submissions """
        queryset = models.Volcano.objects
        height = self.request.query_params.get('height', None)
        if height is not None and height is not '':
            queryset = queryset.filter(Q(height__lte=height))
        else:
            queryset = queryset.all()

        return queryset


class MethodViewSet(viewsets.ModelViewSet):
    queryset = models.Method.objects.all()
    serializer_class = serializers.MethodSerializer
    permission_classes = [permissions.IsAdminLocal]


class TechniqueViewSet(viewsets.ModelViewSet):
    queryset = models.Technique.objects.all()
    serializer_class = serializers.TechniqueSerializer
    permission_classes = [permissions.IsPrincipalOwnTechniqueLocal]


class ParameterViewSet(viewsets.ModelViewSet):
    queryset = models.Parameter.objects.all()
    serializer_class = serializers.ParameterSerializer
    permission_classes = [permissions.IsOwner]

    def get_queryset(self):
        queryset = models.Parameter.objects.all().order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    permission_classes = [permissions.IsPrincipalOwnerMethodByTechnique]

    def get_queryset(self):
        """ allow rest api to filter by submissions """
        queryset = models.Template.objects

        # print self.request
        # print self.request.user.id
        # print self.request.user.method
        # print self.request.user.role
        is_superuser = self.request.user.is_superuser
        is_principal = self.request.user.is_principal
        query = Q()
        anyQuery = False
        if is_superuser:
            state = self.request.query_params.get('state', None)
            technique = self.request.query_params.get('techniqueId', None)
            method = self.request.query_params.get('methodId', None)
            if state is not None and state.capitalize() in ['True', 'False']:
                anyQuery = True
                query = query & Q(state=state.capitalize())
            if technique is not None and technique is not '':
                anyQuery = True
                try:
                    query = query & Q(technique=int(technique))
                except:
                    pass
            if method is not None and method is not '':
                anyQuery = True
                try:
                    query = query & Q(technique__method__id=int(method))
                except:
                    pass
        elif is_principal:
            method = self.request.user.method
            if method is None:
                return []
            anyQuery = True
            query_aux = Q(technique__method__id=int(method.id))
            role = self.request.user.role
            if role and role != '':
                roles = role.split(',')
                print roles
                for rol in roles:
                    query_aux = query_aux | Q(technique=int(rol))
            query = (Q(state=True) | Q(owner=self.request.user.id)) & query_aux

            _method = self.request.query_params.get('methodId', None)
            if _method is not None:
                queryset = queryset.filter(Q(technique__method__id=int(_method)))

        else:
            anyQuery = True
            query_aux = Q()
            role = self.request.user.role
            if role and role != '':
                roles = role.split(',')
                print roles
                for rol in roles:
                    query_aux = query_aux | Q(technique=int(rol))
            query = (Q(state=True) | Q(owner=self.request.user.id)) & query_aux

            _method = self.request.query_params.get('methodId', None)
            if _method is not None:
                queryset = queryset.filter(Q(technique__method__id=int(_method)))

        if anyQuery:
            queryset = queryset.filter(query).order_by('-updated_at')
        else:
            queryset = queryset.all().order_by('-updated_at')
        return queryset

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    # def update(self, request, *args, **kwargs):
    #     print 'UPDATE'
    #     pass

    # def partial_update(self, request, *args, **kwargs):
    #     print '{partial_update}'
    #     # print self.permission_classes[0].has_object_permission(self, request=request)
    #
    #     pk = kwargs.get('pk')
    #     data = request.data
    #     instance = self.queryset.get(pk=pk)
    #     serializer_aux = self.serializer_class(instance=instance)
    #     records = serializer_aux.data.get('records')
    #     serializer = self.serializer_class(instance=instance, data=data, partial=True)
    #     if serializer.is_valid():
    #         if len(records) > 0:
    #             if instance.technique.id == data.get('technique') and instance.volcano.id == data.get('volcano'):
    #                 serializer.save()
    #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
    #             else:
    #                 return Response({'error': 'No puede modificar la "Tecnica" o "Volcan", en una plantilla con registros.'}, status=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RowDefinitiveViewSet(viewsets.ModelViewSet):
    queryset = models.RowDefinitive.objects.all()
    serializer_class = serializers.RowDefinitiveSerializer
    permission_classes = [permissions.IsRowDefinitive]
    pagination_class = DefaultPagination

    def get_queryset(self):

        queryset = models.RowDefinitive.objects

        is_single_insert = self.request.query_params.get('isSingleInsert', None)
        owner = self.request.query_params.get('owner', None)
        hours = self.request.query_params.get('hours', None)
        minutes = self.request.query_params.get('minutes', None)
        template = self.request.query_params.get('templateId', None)

        query = Q()
        anyQuery = False
        if is_single_insert is not None and is_single_insert.capitalize() in ['True', 'False']:
            anyQuery = True
            query = query & Q(is_single_insert=is_single_insert.capitalize())
        if owner is not None and owner is not '':
            anyQuery = True
            try:
                query = query & Q(owner=int(owner))
            except:
                pass
        if template is not None and template is not '':
            anyQuery = True
            try:
                query = query & Q(template=int(template))
            except:
                pass

        if hours is not None or minutes is not None:
            anyQuery = True
            try:
                hours = int(hours)
            except:
                hours = 0

            try:
                minutes = int(minutes)
            except:
                minutes = 0

            today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
            # today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min) - datetime.timedelta(hours=5)
            time_threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=hours, minutes=minutes)
            if today < time_threshold:
                time_threshold_str = time_threshold.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                time_threshold_str = today.strftime("%Y-%m-%dT%H:%M:%SZ")

            print time_threshold_str
            query = query & Q(created_at__gt=time_threshold_str)

        if anyQuery:
            queryset = queryset.filter(query).order_by('-date')
        else:
            queryset = queryset.all().order_by('-date')

        return queryset

    def create(self, request, *args, **kwargs):
        values = None
        if 'values' in request.data:
            values = request.data.get('values')
            request.data.pop('values')

        data = request.data
        serializer = serializers.RowDefinitiveSerializer(data=data)
        if serializer.is_valid():
            row = serializer.save(owner=self.request.user)

            if values is not None:
                RDDSerializer = serializers.RowDefinitiveDataSerializer

                listValues = []
                for itemData in values:
                    itemData['row_definitive'] = row.id
                    print itemData['row_definitive']
                    print itemData
                    print '-------------'
                    listValues.append(itemData)

                rowDataSerializer = RDDSerializer(data=listValues, many=True)
                if rowDataSerializer.is_valid():
                    rowDataSerializer.save()
                else:
                    print rowDataSerializer.errors
                    row.delete()
                    return Response(rowDataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            print 'rikardocorp'
            print instance
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
    # def perform_create(self, serializer):
    #     return serializer.save(owner=self.request.user)


class RowDefinitiveDataViewSet(viewsets.ModelViewSet):
    queryset = models.RowDefinitiveData.objects.all()
    serializer_class = serializers.RowDefinitiveDataSerializer

    # def get_context_data(self, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #     # context['publisher'] = self.object
    #     print 'get_context_data'
    #     print context
    #     return context

    def get_queryset(self):
        # dateFrom = self.request.GET.get('dateFrom', None)
        # dateTo = self.request.GET.get('dateTo', None)
        # filter = self.request.GET.get('filter', None)
        # print 'TEST querySSET'
        # print dateFrom
        # print dateTo
        # print filter
        # print self.request.POST
        # print self.request.POST.get('dateFrom', None)
        # list_data = None
        # if 'dateFrom' in self.request.data:
        #     list_data = self.request.data.get('list')
        # print 'dateFrom'
        # print list_data

        queryset = models.RowDefinitiveData.objects

        template = self.request.query_params.get('templateId', None)
        parameter = self.request.query_params.get('parameterId', None)

        query = Q()
        anyQuery = False
        if template is not None and template is not '':
            anyQuery = True
            try:
                query = query & Q(row_definitive__template__id=int(template))
            except:
                pass

        if parameter is not None and parameter is not '':
            anyQuery = True
            try:
                query = query & Q(parameter=int(parameter))
            except:
                pass

        if anyQuery:
            queryset = queryset.filter(query).order_by('row_definitive__date')
        else:
            queryset = queryset.all().order_by('row_definitive__date')

        return queryset


class UploadFileDataViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsUploadFile]

    def get_object(self, pk):
        try:
            return models.RowDefinitive.objects.get(pk=pk)
        except:
            return None

    def list(self, request):
        queryset = models.RowDefinitive.objects
        is_single_insert = self.request.query_params.get('isSingleInsert', None)
        owner = self.request.query_params.get('owner', None)
        hours = self.request.query_params.get('hours', 0)
        minutes = self.request.query_params.get('minutes', 0)
        template = self.request.query_params.get('templateId', None)

        query = Q()
        anyQuery = True
        if is_single_insert is not None and is_single_insert.capitalize() in ['True', 'False']:
            # anyQuery = True
            query = query & Q(is_single_insert=is_single_insert.capitalize())
        if owner is not None and owner is not '':
            # anyQuery = True
            try:
                query = query & Q(owner=int(owner))
            except:
                pass
        if template is not None and template is not '':
            # anyQuery = True
            print 'template'
            try:
                query = query & Q(template=int(template))
            except:
                pass

        try:
            hours = int(hours)
        except:
            hours = 0

        try:
            minutes = int(minutes)
        except:
            minutes = 0

        # time_threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
        # today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min) - datetime.timedelta(hours=5)
        time_threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=hours, minutes=minutes)
        if today < time_threshold:
            time_threshold_str = time_threshold.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            time_threshold_str = today.strftime("%Y-%m-%dT%H:%M:%SZ")

        # print datetime.datetime.utcnow()
        # print time_threshold
        # print time_threshold_str
        # print aux
        query = query & Q(created_at__gt=time_threshold_str)

        if anyQuery:
            queryset = queryset.filter(query).order_by('-created_at')
        else:
            queryset = queryset.all().order_by('-created_at')

        serializer = serializers.RowDefinitiveSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.RowDefinitive.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = serializers.RowDefinitiveSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        data_total = None
        if 'data' in request.data:
            data_total = request.data.get('data')

        print 'DATA-TOTAL-UPLOAD'
        ERROR_LIST = []
        SUCCESS_LIST = []
        if data_total is not None:
            values = None
            for index, dataItem in enumerate(data_total):
                values = dataItem.pop('values')
                # print values
                # print dataItem
                data = dataItem
                data['is_single_insert'] = False
                data['date'] = data['date'][:19]
                print data
                print '-------------'
                serializer = serializers.RowDefinitiveSerializer(data=data)
                if serializer.is_valid():
                    row = serializer.save(owner=self.request.user)
                    if values is not None:
                        RDDSerializer = serializers.RowDefinitiveDataSerializer
                        listValues = []
                        for itemData in values:
                            itemData['row_definitive'] = row.id
                            listValues.append(itemData)

                        rowDataSerializer = RDDSerializer(data=listValues, many=True)
                        if rowDataSerializer.is_valid():
                            rowDataSerializer.save()
                            SUCCESS_LIST.append({'index': index, 'id': serializer.data['id'], 'date': data['date']})
                        else:
                            print rowDataSerializer.errors
                            row.delete()
                            ERROR_LIST.append({'index': index, 'date': data['date'], 'error': rowDataSerializer.errors})
                else:
                    ERROR_LIST.append({'index': index, 'date': data['date'], 'error': serializer.errors})

            response_data = {
                'success_data': {
                    'total': len(SUCCESS_LIST), 'data': SUCCESS_LIST
                },
                'error_data': {
                    'total': len(ERROR_LIST), 'data': ERROR_LIST
                }
            }

            if len(ERROR_LIST) == 0:
                response_data['message'] = 'Se registraron todos los datos del archivo.'
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data['message'] = 'Algunos datos del archivo no fueron registrados.'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('No hay datos', status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        print 'DESTROY [Rikardocorp]'
        print request.data
        list_data = None
        if 'list' in request.data:
            list_data = request.data.get('list')

        if isinstance(list_data, list) and len(list_data) > 0:
            print list_data
            ERROR_LIST = []
            SUCCESS_LIST = []

            for idDelete in list_data:
                print idDelete
                try:
                    instance = models.RowDefinitive.objects.get(pk=idDelete)
                    instance.delete()
                    SUCCESS_LIST.append(idDelete)
                except:
                    ERROR_LIST.append(idDelete)

            response_data = {
                'success_data': {
                    'total': len(SUCCESS_LIST), 'data': SUCCESS_LIST
                },
                'error_data': {
                    'total': len(ERROR_LIST), 'data': ERROR_LIST
                }
            }

            print 'ERROR LIST'
            print ERROR_LIST

            if len(ERROR_LIST) == 0:
                response_data['message'] = 'Los registros seleccionados fueron eliminados.'
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                print 'ERROR LIST Response'
                response_data['message'] = 'Algunos de los registros no fueron eliminados, intentar nuevamente o verificar sus permisos de usuario.'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Debe seleccionar las filas que desea eliminar.', status=status.HTTP_400_BAD_REQUEST)


upload_file_data_list = UploadFileDataViewSet.as_view({'get': 'list', 'post': 'create'})
upload_file_data_detail = UploadFileDataViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})


import csv
from django.http import HttpResponse


@api_view(['GET', 'POST'])
@permission_classes((AllowAny, ))
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        responseCSV = request.query_params.get('CSV', False)
        if responseCSV is not None and responseCSV in ['True', 'true']:
            responseCSV = True
        else:
            responseCSV = False
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        # writer = csv.writer(response)
        # writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
        # writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
        #
        # return response
        data = models.RowDefinitive.objects.all()
        serializer = serializers.RowDefinitiveSerializer(data, many=True)

        if responseCSV:
            data = serializer.data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="result.csv"'
            writer = csv.writer(response)
            # writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
            for item in data:
                template_order = item['template_order'].split(',')
                values = item['data']
                objValues = {}
                for val in values:
                    objValues[val['parameter']] = val['value']

                stringRow = [item['date']]
                for order in template_order:
                    try:
                        valOrder = objValues[int(order)]
                    except:
                        valOrder = ''

                    stringRow.append(valOrder)
                writer.writerow(stringRow)

                print objValues
                print template_order
                print stringRow
            return response
        else:
            result = serializer.data
            return Response(result, status=status.HTTP_202_ACCEPTED)

    elif request.method == 'POST':
        responseCSV = request.query_params.get('CSV', False)
        if responseCSV is not None and responseCSV in ['True', 'true']:
            responseCSV = True
        else:
            responseCSV = False

        print 'responseCSV'
        print responseCSV

        templateId = request.data.get('templateId', None)
        datetimeType = request.data.get('datetimeType', 'date')
        dateFrom = request.data.get('dateFrom', None)
        dateTo = request.data.get('dateTo', None)
        volcanoId = request.data.get('volcanoId', None)
        owner = request.data.get('owner', None)
        filter = request.data.get('filter', [])
        print 'REQUEST DATA'
        print request.data
        print dateFrom
        print dateTo
        print filter
        print '-----------'
        query = Q()

        if len(filter) == 0:
            if templateId is not None and templateId != '':
                query = query & Q(template=int(templateId))

            if datetimeType == 'date':
                if dateFrom is not None:
                    query = query & Q(date__gte=dateFrom + 'Z')

                if dateTo is not None:
                    query = query & Q(date__lte=dateTo + 'Z')
            if datetimeType == 'created_at':
                if dateFrom is not None:
                    query = query & Q(created_at__gte=dateFrom + 'Z')

                if dateTo is not None:
                    query = query & Q(created_at__lte=dateTo + 'Z')

            if volcanoId is not None and volcanoId != '':
                query = query & Q(volcano=int(volcanoId))

            if owner is not None and owner != '':
                query = query & Q(owner=int(owner))

            queryset = models.RowDefinitive.objects.filter(query)

        else:
            if datetimeType == 'date':
                if dateFrom is not None:
                    query = query & Q(row_definitive__date__gte=dateFrom + 'Z')

                if dateTo is not None:
                    query = query & Q(row_definitive__date__lte=dateTo + 'Z')
            if datetimeType == 'created_at':
                if dateFrom is not None:
                    query = query & Q(row_definitive__created_at__gte=dateFrom + 'Z')

                if dateTo is not None:
                    query = query & Q(row_definitive__created_at__lte=dateTo + 'Z')

            total_filter = len(filter)
            query_filter = Q()
            for item in filter:
                query_values = Q()
                if item['valueFrom'] is not None:
                    query_values = query_values & Q(value__gte=int(item['valueFrom']))

                if item['valueTo'] is not None:
                    query_values = query_values & Q(value__lte=int(item['valueTo']))

                print item
                query_filter = query_filter | (Q(parameter=int(item['parameterId'])) & query_values)

            query = query & query_filter

            queryset_aux = models.RowDefinitiveData.objects
            rows_data = queryset_aux.filter(query).values('row_definitive').annotate(total=Count('row_definitive')).order_by('row_definitive')
            rows_data_result = rows_data.filter(Q(total__gte=total_filter)).values('row_definitive')
            list_id = [x['row_definitive'] for x in rows_data_result]
            queryset = models.RowDefinitive.objects.filter(id__in=list_id)

        queryset = queryset.order_by('-' + datetimeType)
        serializer = serializers.RowDefinitiveSerializer(queryset, many=True)

        if responseCSV:
            data = serializer.data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="result.csv"'
            writer = csv.writer(response)
            # writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
            for item in data:
                template_order = item['template_order'].split(',')
                values = item['data']
                objValues = {}
                for val in values:
                    objValues[val['parameter']] = val['value']

                stringRow = [item['date']]
                for order in template_order:
                    try:
                        valOrder = objValues[int(order)]
                    except:
                        valOrder = ''

                    stringRow.append(valOrder)
                writer.writerow(stringRow)

                print objValues
                print template_order
                print stringRow
            return response
        else:
            result = serializer.data
            return Response(result, status=status.HTTP_200_OK)

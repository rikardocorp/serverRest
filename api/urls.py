from django.conf.urls import url, include

from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'volcano', views.VolcanoViewSet)
router.register(r'method', views.MethodViewSet)
router.register(r'technique', views.TechniqueViewSet)
router.register(r'parameter', views.ParameterViewSet)
router.register(r'template', views.TemplateViewSet)
router.register(r'rowdefinitive', views.RowDefinitiveViewSet)
router.register(r'rowdefinitivedata', views.RowDefinitiveDataViewSet)

router.register(r'uploadfiledata', views.UploadFileDataViewSet, basename='upload_file_data')
urlpatterns = [
    url(r'^', include(router.urls)),
    url('search_data/', views.snippet_list),
]
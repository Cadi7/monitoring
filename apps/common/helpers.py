from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["https", "http"]
        return schema


schema_view = get_schema_view(
    info=openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Enjoy",
    ),
    validators=['ssv'],
    generator_class=BothHttpAndHttpsSchemaGenerator,
    public=True,
    permission_classes=[AllowAny, ],
)


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'size'

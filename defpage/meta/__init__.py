from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from defpage.meta.sql import initialize_sql
from defpage.meta.config import system_params

def main(global_config, **settings):
    system_params.update(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator()
    config.setup_registry(settings=settings)

    config.add_route("collections", "/collections/")
    config.add_route("collection", "/collections/{collection_id}")

    config.add_route("documents", "/documents/")
    config.add_route("document", "/documents/{document_id}")

    config.add_view("defpage.meta.views.search_collections", route_name="collections", renderer="json", request_method="GET")
    config.add_view("defpage.meta.views.get_collection", route_name="collection", renderer="json", request_method="GET")
    config.add_view("defpage.meta.views.add_collection", route_name="collections", renderer="json", request_method="POST")
    config.add_view("defpage.meta.views.edit_collection", route_name="collection", request_method="PUT")

    return config.make_wsgi_app()

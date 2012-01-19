from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from defpage.auth.sql import initialize_sql
from defpage.auth.config import system_params

def main(global_config, **settings):
    system_params.update(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator()
    config.setup_registry(settings=settings)

    config.add_route("sessions", "/users/{user_id}")
    config.add_route("collections", "/collections/{collection_id}")
    config.add_route("docs", "/docs/{document_id}")

    config.add_view("defpage.meta.views.get_user", route_name="users", renderer="json", request_method="GET")

    return config.make_wsgi_app()

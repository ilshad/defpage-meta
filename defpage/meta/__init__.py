from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from defpage.lib.authentication import BasicAuthenticationPolicy
from defpage.lib.util import is_int
from defpage.meta.config import system_params
from defpage.meta.sql import initialize_sql
from defpage.meta.security import security_checker
from defpage.meta.resources import get_collection
from defpage.meta.resources import get_document

def main(global_config, **settings):
    system_params.update(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator()
    authentication_policy=BasicAuthenticationPolicy(security_checker)
    config.setup_registry(settings=settings, authentication_policy=authentication_policy)

    config.add_route("cols", "/collections/")

    config.add_route("col", "/collections/{name}",
                     factory=get_collection, custom_predicates=(is_int,))

    config.add_route("docs", "/documents/")

    config.add_route("doc", "/documents/{name}",
                     factory=get_document, custom_predicates=(is_int,))

    # collections
    config.add_view("defpage.meta.views.add_collection",
                    route_name="cols", renderer="json", request_method="POST")

    config.add_view("defpage.meta.views.edit_collection",
                    route_name="col", request_method="PUT", permission="manage")

    config.add_view("defpage.meta.views.del_collection",
                    route_name="col", request_method="DELETE", permission="delete")

    config.add_view("defpage.meta.views.get_collection",
                    route_name="col", renderer="json", request_method="GET", permission="view")

    config.add_view("defpage.meta.views.search_collections",
                    route_name="cols", renderer="json", request_method="GET")

    # documents
    config.add_view("defpage.meta.views.add_document",
                    route_name="docs", renderer="json", request_method="POST")

    config.add_view("defpage.meta.views.edit_document",
                    route_name="doc", request_method="PUT")

    config.add_view("defpage.meta.views.del_document",
                    route_name="doc", request_method="DELETE")

    config.add_view("defpage.meta.views.get_document",
                    route_name="doc", renderer="json", request_method="GET")

    return config.make_wsgi_app()

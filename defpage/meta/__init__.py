from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from defpage.lib.authentication import BasicAuthenticationPolicy
from defpage.meta.config import system_params
from defpage.meta.security import security_checker
from defpage.meta import tree
from defpage.meta import sql

def main(global_config, **settings):
    system_params.update(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    sql.initialize_sql(engine)
    authentication_policy=BasicAuthenticationPolicy(security_checker)
    config = Configurator()
    config.setup_registry(settings=settings, root_factory=tree.root_factory, authentication_policy=authentication_policy)

    config.add_view("defpage.meta.views.add_collection", context=tree.Collections, renderer="json", request_method="POST")
    config.add_view("defpage.meta.views.edit_collection", context=sql.Collection, request_method="PUT", permission="manage")
    config.add_view("defpage.meta.views.del_collection", context=sql.Collection, request_method="DELETE", permission="manage")
    config.add_view("defpage.meta.views.get_collection", context=sql.Collection, renderer="json", request_method="GET", permission="view")
    config.add_view("defpage.meta.views.search_collections", context=tree.Collections, renderer="json", request_method="GET")

    config.add_view("defpage.meta.views.add_document", context=tree.Documents, renderer="json", request_method="POST")
    config.add_view("defpage.meta.views.edit_document", context=sql.Document, request_method="PUT")
    config.add_view("defpage.meta.views.del_document", context=sql.Document, request_method="DELETE")
    config.add_view("defpage.meta.views.get_document", context=sql.Document, renderer="json", request_method="GET")

    return config.make_wsgi_app()

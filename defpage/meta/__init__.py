from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from defpage.lib.authentication import BasicAuthenticationPolicy
from defpage.lib.util import is_int
from defpage.meta.config import system_params
from defpage.meta.sql import initialize_sql
from defpage.meta.security import security_checker
from defpage.meta.resources import get_collection
from defpage.meta.resources import get_document
from defpage.meta.resources import get_source

def main(global_config, **settings):
    system_params.update(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator()
    authentication_policy=BasicAuthenticationPolicy(security_checker)

    config.setup_registry(settings=settings,
                          authentication_policy=authentication_policy)

    config.add_route("collections", "/collections/")

    config.add_route("collection", "/collections/{name}",
                     factory=get_collection,
                     custom_predicates=(is_int,))

    config.add_route("collection_transmissions", "/collections/{name}/transmissions/",
                     factory=get_collection,
                     custom_predicates=(is_int,))

    config.add_route("transmission", "/collections/{name}/transmissions/{id}",
                     factory=get_collection,
                     custom_predicates=(is_int,))

    config.add_route("collection_documents", "/collections/{name}/documents/",
                     factory=get_collection,
                     custom_predicates=(is_int,))

    config.add_route("documents", "/documents/")

    config.add_route("document", "/documents/{name}",
                     factory=get_document,
                     custom_predicates=(is_int,))

    config.add_route("sources", "/sources/{name}/{source_type}",
                     factory=get_source,
                     custom_predicates=(is_int,))

    config.add_route("document_transmissions_directory", "/documents/{name}/transmissions/",
                     factory=get_document,
                     custom_predicates=(is_int,))

    config.add_route("document_transmission", "/documents/{name}/transmissions/{id}",
                     factory=get_document,
                     custom_predicates=(is_int,))

    config.add_view("defpage.meta.views.add_collection",
                    route_name="collections",
                    renderer="json",
                    request_method="POST")

    config.add_view("defpage.meta.views.edit_collection",
                    route_name="collection",
                    request_method="POST",
                    permission="manage")

    config.add_view("defpage.meta.views.del_collection",
                    route_name="collection",
                    request_method="DELETE",
                    permission="delete")

    config.add_view("defpage.meta.views.get_collection",
                    route_name="collection",
                    renderer="json",
                    request_method="GET",
                    permission="view")

    config.add_view("defpage.meta.views.get_collection_documents",
                    route_name="collection_documents",
                    renderer="json",
                    request_method="GET",
                    permission="view")

    config.add_view("defpage.meta.views.search_collections",
                    route_name="collections",
                    renderer="json",
                    request_method="GET")

    config.add_view("defpage.meta.views.add_document",
                    route_name="documents",
                    renderer="json",
                    request_method="POST")

    config.add_view("defpage.meta.views.edit_document",
                    route_name="document",
                    request_method="POST")

    config.add_view("defpage.meta.views.del_document",
                    route_name="document",
                    request_method="DELETE")

    config.add_view("defpage.meta.views.get_document",
                    route_name="document",
                    renderer="json",
                    request_method="GET")

    config.add_view("defpage.meta.views.set_source",
                    route_name="sources",
                    request_method="POST")

    config.add_view("defpage.meta.views.add_transmission",
                    route_name="collection_transmissions",
                    request_method="POST",
                    permission="manage")

    config.add_view("defpage.meta.views.get_collection_transmissions",
                    route_name="collection_transmissions",
                    renderer="json",
                    request_method="GET",
                    permission="manage")

    config.add_view("defpage.meta.views.get_transmission",
                    route_name="transmission",
                    renderer="json",
                    request_method="GET",
                    permission="manage")

    config.add_view("defpage.meta.views.put_transmission",
                    route_name="transmission",
                    request_method="PUT",
                    permission="manage")

    config.add_view("defpage.meta.views.delete_transmission",
                    route_name="transmission",
                    request_method="DELETE",
                    permission="manage")

    config.add_view("defpage.meta.views.get_document_transmissions_directory",
                    route_name="document_transmissions_directory",
                    renderer="json",
                    request_method="GET")

    config.add_view("defpage.meta.views.get_document_transmission",
                    route_name="document_transmission",
                    renderer="json",
                    request_method="GET")

    config.add_view("defpage.meta.views.add_document_transmission",
                    route_name="document_transmissions_directory",
                    request_method="POST")

    config.add_view("defpage.meta.views.update_document_transmission",
                    route_name="document_transmission",
                    request_method="PUT")

    config.add_view("defpage.meta.views.delete_document_transmission",
                    route_name="document_transmission",
                    request_method="DELETE")

    return config.make_wsgi_app()

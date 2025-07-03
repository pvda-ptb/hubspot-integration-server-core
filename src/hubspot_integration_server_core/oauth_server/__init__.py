from flask import Flask, Blueprint
from .handlers import oauth_callback, process_oauth, success
from ..database import db
from ..config import HubspotIntegrationConfig
from hubspot import Client

from hubspot_integration_server_core.models import HubspotCredentials

def _custom_api_factory(api_client_package, api_name, config):
    configuration = api_client_package.Configuration()
    for key in config:
        if key == "retry":
            configuration.retries = config["retry"]
        else:
            setattr(configuration, key, config[key])

    api_client = api_client_package.ApiClient(configuration=configuration)
    # package_version = metadata.version("hubspot-api-client")
    # api_client.user_agent = "hubspot-api-client-python; {0}".format(package_version)

    return getattr(api_client_package, api_name)(api_client=api_client)


class OAuthServer:
    def __init__(self, app: Flask, config: HubspotIntegrationConfig):
        self.config = config

        self.oauth_blueprint = Blueprint('oauth', __name__)

        self.api_client = Client(
            client_id=config.hubspot_client_id,
            client_secret=config.hubspot_client_secret,
            api_factory=_custom_api_factory,
        )

        self.oauth_blueprint.custom_oauth_form = config.oauth_server_custom_form
        self.oauth_blueprint.oauth_server = self

        self.oauth_blueprint.add_url_rule("/oauth/callback", view_func=oauth_callback, methods=["GET"])
        self.oauth_blueprint.add_url_rule("/oauth/process", view_func=process_oauth, methods=["POST"])
        self.oauth_blueprint.add_url_rule("/oauth/success", view_func=success, methods=["GET"])

        app.register_blueprint(self.oauth_blueprint)

    def process_tokens(self, credentials_data: dict, form_data: dict=None):
        credentials = HubspotCredentials(**credentials_data)

        db.session.add(credentials)
        db.session.commit()

        print("New account created with ID:", credentials.id)

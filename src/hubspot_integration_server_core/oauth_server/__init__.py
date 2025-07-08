from typing import Optional

from flask import Flask, Blueprint
from .handlers import oauth_callback, process_oauth, success
from ..database import db
from hubspot import Client

from hubspot_integration_server_core.models import HubspotCredentials


class OAuthServer:
    oauth_server_custom_form: Optional[str] = None

    def __init__(self, app: Flask, config: dict):
        self.config = config

        self.oauth_blueprint = Blueprint('oauth', __name__)

        self.api_client = Client(
            client_id=config['HUBSPOT_CLIENT_ID'],
            client_secret=config['HUBSPOT_CLIENT_SECRET'],
        )

        self.oauth_blueprint.custom_oauth_form = self.oauth_server_custom_form
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

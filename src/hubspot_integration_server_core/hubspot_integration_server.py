import os
import logging
from typing import Type
from flask import Flask

from .config import HubspotIntegrationConfig
from .database import db
from .utils import validate_hubspot_signature
from .oauth_server import OAuthServer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set logging level to debug

class HubspotIntegrationServer:
    """
    Core server class for integrating with HubSpot.

    Handles initialization of services like Flask, SQLAlchemy, and OAuth server.
    """

    def __init__(
            self,
            config: HubspotIntegrationConfig,
            oauth_server_class: Type[OAuthServer] = OAuthServer,
    ):
        """
        Initializes the integration server with the given configuration.

        :param config: The configuration object for HubSpot integration.
        :param oauth_server_class: Class reference for OAuth server initialization.
        """
        self.config = config
        self._oauth_server_class = oauth_server_class

        try:
            self._initialize_services()
            logger.debug("Services initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize services: {e}")

    def _initialize_services(self):
        """
        Initializes the core services: Flask app, SQLAlchemy, and OAuth server.

        Each initialization step includes error handling and logging.
        """
        try:
            # Initialize Flask app
            self.app = Flask(
                __name__,
                root_path=self.config.flask_base_path,
                template_folder=os.path.join(self.config.flask_base_path, self.config.flask_template_folder),
                instance_path=os.path.join(self.config.flask_base_path, self.config.flask_instance_path),
            )
            logger.debug("Flask app initialized.")
        except Exception as e:
            logger.exception(f"Failed to initialize Flask app: {e}")
            raise

        try:
            # Initialize SQLAlchemy
            self.app.config['SQLALCHEMY_DATABASE_URI'] = self.config.database_uri
            self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            db.init_app(self.app)
            logger.debug("SQLAlchemy initialized with URI: %s", self.config.database_uri)
        except Exception as e:
            logger.exception(f"Failed to initialize SQLAlchemy: {e}")
            raise

        try:
            # Initialize OAuth server
            self.oauth_server = self._oauth_server_class(self.app, self.config)
            logger.debug("OAuth server initialized.")
        except Exception as e:
            logger.exception(f"Failed to initialize OAuth server: {e}")
            raise

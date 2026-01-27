import os
import logging
from typing import Type
from flask import Flask

from .database import db
from .oauth_server import OAuthServer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set logging level to debug


class HubspotIntegrationServer(Flask):
    """
    Core server class for integrating with HubSpot.

    Handles initialization of services like Flask, SQLAlchemy, and OAuth server.
    """

    def __init__(
            self,
            config: dict,
            oauth_server_class: Type[OAuthServer] = OAuthServer,
    ):
        """
        Initializes the integration server with the given configuration.

        :param config: The configuration object for HubSpot integration.
        :param oauth_server_class: Class reference for OAuth server initialization.
        """
        root_path = os.getenv('FLASK_BASE_PATH', os.getcwd())
        instance_path=os.path.join(root_path, os.getenv('FLASK_INSTANCE_PATH', 'instance'))
        template_folder=os.path.join(root_path, os.getenv('FLASK_TEMPLATE_FOLDER', 'templates'))
        super().__init__(
            __name__,
            root_path=root_path,
            instance_path=instance_path,
            template_folder=template_folder,
        )
        self.config.update(config)
        self._oauth_server_class = oauth_server_class

        try:
            self._initialize_services()
            logger.debug("Services initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize services: {e}")

    def _initialize_services(self):
        """
        Initializes the core services: SQLAlchemy and OAuth server.

        Each initialization step includes error handling and logging.
        """
        try:
            # Initialize SQLAlchemy
            self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            db.init_app(self)
            logger.debug("SQLAlchemy initialized with URI: %s", self.config['SQLALCHEMY_DATABASE_URI'])
        except Exception as e:
            logger.exception(f"Failed to initialize SQLAlchemy: {e}")
            raise

        try:
            # Initialize OAuth server
            self.oauth_server = self._oauth_server_class(self, self.config)
            logger.debug("OAuth server initialized.")
        except Exception as e:
            logger.exception(f"Failed to initialize OAuth server: {e}")
            raise
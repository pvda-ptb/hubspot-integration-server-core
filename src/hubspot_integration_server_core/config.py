import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class HubspotIntegrationConfig:
    """
    Configuration class for HubSpot integration.

    Provides application-wide configuration settings.
    """

    def __init__(
            self,
            root_url: Optional[str] = None,
            hubspot_client_id: Optional[str] = None,
            hubspot_client_secret: Optional[str] = None,
            hubspot_oauth_redirect_url: Optional[str] = None,
            hubspot_developer_hapikey: Optional[str] = None,
            hubspot_app_id: Optional[str] = None,
            database_uri: Optional[str] = None,
            flask_base_path: Optional[str] = None,
            flask_template_folder: str = 'templates',
            flask_instance_path: str = 'instance',
            oauth_server_custom_form: str = None,
    ):
        """
        Initialize configuration with optional overrides and environment variables.
        """
        self.root_url = root_url or os.getenv('ROOT_URL')
        logger.debug(f"Set root_url: {self.root_url}")

        # Load HubSpot configuration
        self.hubspot_client_id = hubspot_client_id or os.getenv('HUBSPOT_CLIENT_ID')
        self.hubspot_client_secret = hubspot_client_secret or os.getenv('HUBSPOT_CLIENT_SECRET')
        self.hubspot_oauth_redirect_url = hubspot_oauth_redirect_url or os.getenv('HUBSPOT_OAUTH_REDIRECT_URL')
        self.hubspot_developer_hapikey = hubspot_developer_hapikey or os.getenv('HUBSPOT_DEVELOPER_HAPIKEY')
        self.hubspot_app_id = hubspot_app_id or os.getenv('HUBSPOT_APP_ID')

        # Log the HubSpot app ID and key
        logger.debug(f"HubSpot client_id: {self.hubspot_client_id}")
        logger.debug(f"HubSpot app_id: {self.hubspot_app_id}")

        # Load Database configuration
        self.database_uri = database_uri or os.getenv('DATABASE_URI')
        logger.debug(f"Database URI: {self.database_uri}")

        # Flask application paths
        self.flask_base_path = flask_base_path or os.getcwd()
        self.flask_template_folder = flask_template_folder
        self.flask_instance_path = flask_instance_path
        logger.debug(f"Flask base path: {self.flask_base_path}")

        self.oauth_server_custom_form = oauth_server_custom_form

        # Validate required fields
        self.validate_required_fields()

    def validate_required_fields(self):
        """
        Validate that all required configuration fields are provided.
        """
        if not self.hubspot_client_id:
            logger.error("HubSpot client ID is missing")
            raise ValueError("HubSpot client ID must be provided")
        if not self.hubspot_client_secret:
            logger.error("HubSpot client secret is missing")
            raise ValueError("HubSpot client secret must be provided")
        if not self.hubspot_oauth_redirect_url:
            logger.error("HubSpot OAuth redirect URL is missing")
            raise ValueError("HubSpot OAuth redirect URL must be provided")
        if not self.database_uri:
            logger.error("Database URI is missing")
            raise ValueError("Database URI must be provided")

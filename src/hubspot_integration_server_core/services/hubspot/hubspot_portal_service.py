import logging
from hubspot import OAuthClient
from sqlalchemy.orm.exc import NoResultFound

from ...config import HubspotIntegrationConfig
from ...database import db
from ...models import HubspotCredentials

# Create or retrieve a logger instance
logger = logging.getLogger(__name__)

class HubspotPortalService:
    def __init__(self, config: HubspotIntegrationConfig):
        """Initializes the HubspotPortalService with the given configuration."""
        self.config = config

    def get_hubspot_client(self, credentials: HubspotCredentials):
        """
        Returns an OAuth client configured with the given Hubspot credentials.

        If the access token is refreshed, the credentials in the database are updated.
        """
        def access_token_setter_callback(new_tokens):
            logger.debug("Access token will be updated in the database.")
            credentials.hubspot_access_token = new_tokens.access_token
            credentials.hubspot_expires_in = new_tokens.expires_in
            db.session.add(credentials)
            db.session.commit()
            logger.debug("Access token updated successfully.")

        try:
            hubspot_client = OAuthClient(
                client_id=self.config.hubspot_client_id,
                client_secret=self.config.hubspot_client_secret,
                refresh_token=credentials.hubspot_refresh_token,
                access_token=credentials.hubspot_access_token,
                portal_id=credentials.hubspot_portal_id,
                access_token_setter_callback=access_token_setter_callback,
            )
            logger.debug("Hubspot OAuth client created successfully.")
            return hubspot_client
        except Exception as e:
            logger.error(f"Failed to create Hubspot OAuth client: {e}")
            raise

    def get_hubspot_client_by_portalid(self, hubspot_portal_id: int):
        """
        Retrieves the OAuth client using the Hubspot portal ID by fetching the
        corresponding credentials from the database.
        
        Logs an error if credentials are not found.
        """
        try:
            credentials = db.session.query(HubspotCredentials).filter_by(hubspot_portal_id=hubspot_portal_id).one()
            logger.debug(f"Credentials retrieved for portal ID {hubspot_portal_id}.")
            return self.get_hubspot_client(credentials)
        except NoResultFound:
            logger.error(f"No credentials found for portal ID {hubspot_portal_id}.")
            raise
        except Exception as e:
            logger.error(f"Error retrieving Hubspot client: {e}")
            raise
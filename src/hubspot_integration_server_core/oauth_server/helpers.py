from ..database import db
from hubspot_integration_server_core.models import HubspotCredentials
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)

def default_oauth_process(code, api_client, config):
    """
    Handles the OAuth process for HubSpot integration.

    :param code: The authorization code received from HubSpot.
    :param api_client: The HubSpot API client instance.
    :param config: Configuration containing HubSpot OAuth settings.
    :return: HubspotCredentials object with saved token details.
    """
    try:
        # Obtain tokens using the authorization code
        tokens = api_client.oauth.tokens_api.create(
            grant_type="authorization_code",
            redirect_uri=config['HUBSPOT_OAUTH_REDIRECT_URL'],
            client_id=config['HUBSPOT_CLIENT_ID'],
            client_secret=config['HUBSPOT_CLIENT_SECRET'],
            code=code
        )
        logger.debug("Received tokens from HubSpot: %s", tokens)

        # Retrieve additional token details
        tokens_details = api_client.oauth.access_tokens_api.get(tokens.access_token)
        logger.debug("Retrieved token details: %s", tokens_details)

        # Prepare credentials data for storage
        credentials_data = {
            "hubspot_portal_id": tokens_details.hub_id,
            "hubspot_portal_domain": tokens_details.hub_domain,
            "hubspot_user_id": tokens_details.user_id,
            "hubspot_user_email": tokens_details.user,
            "hubspot_scopes": ','.join(tokens_details.scopes),
            "hubspot_access_token": tokens.access_token,
            "hubspot_refresh_token": tokens.refresh_token,
            "hubspot_expires_in": tokens_details.expires_in,
        }

        # Save credentials to the database
        credentials = HubspotCredentials.create(**credentials_data)
        logger.debug("HubSpot credentials saved successfully")

        return credentials

    except Exception as e:
        logger.error("Error in the OAuth process: %s", str(e), exc_info=True)
        db.session.rollback()  # Rollback in case of error
        raise e

import logging
from hubspot import Client


# Initialize a logger for this module
logger = logging.getLogger(__name__)

def _custom_api_factory(api_client_package, api_name, config):
    """
    Creates a custom API client using the provided configuration.

    :param api_client_package: The package containing the API client.
    :param api_name: Name of the API service to access.
    :param config: Configuration dictionary for the API client.
    :return: An instance of the specified API client.
    """
    try:
        configuration = api_client_package.Configuration()
        for key in config:
            if key == "retry":
                configuration.retries = config["retry"]
            else:
                setattr(configuration, key, config[key])

        api_client = api_client_package.ApiClient(configuration=configuration)
        return getattr(api_client_package, api_name)(api_client=api_client)
    except Exception as e:
        logger.debug(f"Failed to create custom API client for {api_name}: {e}")
        raise

class HubspotAppService:
    """
    Provides services for interacting with the HubSpot API using the
    specified configuration.
    """

    def __init__(self, config: dict):
        """
        Initializes the HubspotAppService with the given configuration.

        :param config: A HubspotIntegrationConfig instance containing API details.
        """
        self.config = config
        logger.debug("HubspotAppService initialized with config.")

    def get_hubspot_client(self):
        """
        Creates and returns a HubSpot client instance.

        :return: An instance of the HubSpot client.
        :raises: Exception if client creation fails due to invalid configuration.
        """
        try:
            hubspot_client = Client(
                client_id=self.config['HUBSPOT_CLIENT_ID'],
                client_secret=self.config['HUBSPOT_CLIENT_SECRET'],
                api_key={
                    'developer_hapikey': self.config['HUBSPOT_DEVELOPER_HAPIKEY'],
                    'app_id': self.config['HUBSPOT_APP_ID'],
                },
                api_factory=_custom_api_factory,
            )
            logger.debug("Successfully created HubSpot client.")
            return hubspot_client
        except Exception as e:
            logger.debug(f"Failed to create HubSpot client: {e}")
            raise

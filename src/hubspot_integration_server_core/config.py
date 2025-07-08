import os
import logging
from dotenv import load_dotenv

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def load_configuration():
    """Load configurations and return them as a dictionary."""
    # Load environment variables
    load_dotenv()

    config = {
        'ROOT_URL': os.getenv('ROOT_URL'),
        'HUBSPOT_CLIENT_ID': os.getenv('HUBSPOT_CLIENT_ID'),
        'HUBSPOT_CLIENT_SECRET': os.getenv('HUBSPOT_CLIENT_SECRET'),
        'HUBSPOT_OAUTH_REDIRECT_URL': os.getenv('HUBSPOT_OAUTH_REDIRECT_URL'),
        'HUBSPOT_DEVELOPER_HAPIKEY': os.getenv('HUBSPOT_DEVELOPER_HAPIKEY'),
        'HUBSPOT_APP_ID': os.getenv('HUBSPOT_APP_ID'),
        'SQLALCHEMY_DATABASE_URI': os.getenv('SQLALCHEMY_DATABASE_URI'),
        'FLASK_BASE_PATH': os.getcwd(),
        'FLASK_TEMPLATE_FOLDER': 'templates',
        'FLASK_INSTANCE_PATH': 'instance',
    }

    # Log critical values
    logger.debug(f"Loaded configuration: {config}")
    return config

# Call load_configuration and store the result in 'configuration'
configuration = load_configuration()

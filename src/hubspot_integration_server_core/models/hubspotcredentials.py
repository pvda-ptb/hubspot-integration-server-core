from sqlalchemy.exc import SQLAlchemyError
from ..database import db
import logging

logger = logging.getLogger(__name__)

class HubspotCredentials(db.Model):
    """
    ORM model for storing Hubspot credentials in the database.
    
    Attributes:
        id: Primary key for the credentials entry.
        hubspot_portal_id: Unique identifier for the Hubspot portal.
        hubspot_portal_domain: Domain name associated with the Hubspot portal.
        hubspot_user_id: User ID of the Hubspot user.
        hubspot_user_email: Email address of the Hubspot user.
        hubspot_scopes: Scopes granted by the Hubspot OAuth.
        hubspot_access_token: OAuth access token for Hubspot API.
        hubspot_refresh_token: OAuth refresh token for Hubspot API.
        hubspot_expires_in: Token expiration time in seconds.
    """

    id = db.Column(db.Integer, primary_key=True)

    hubspot_portal_id = db.Column(db.Integer, unique=True)
    hubspot_portal_domain = db.Column(db.String(256))
    hubspot_user_id = db.Column(db.Integer)
    hubspot_user_email = db.Column(db.String(256))
    hubspot_scopes = db.Column(db.String(256))  # Scopes are stored as a comma-separated string

    # OAuth fields
    hubspot_access_token = db.Column(db.String(512))
    hubspot_refresh_token = db.Column(db.String(512))
    hubspot_expires_in = db.Column(db.Integer)

    @classmethod
    def get_all_credentials(cls):
        """
        Retrieve all Hubspot credentials from the database.

        Returns:
            A list of HubspotCredentials objects or an empty list if there is an error.
        """
        try:
            credentials = db.session.query(cls).all()
            logger.debug("Retrieved %d Hubspot credentials.", len(credentials))
            return credentials
        except SQLAlchemyError as e:
            logger.error("Failed to retrieve credentials: %s", str(e), exc_info=True)
            return []

    @classmethod
    def get_by_hubspot_portal_id(cls, hubspot_portal_id: int):
        """
        Retrieve a specific Hubspot credential using the portal ID.

        Args:
            hubspot_portal_id: The ID of the Hubspot portal to search for.

        Returns:
            A HubspotCredentials object if found, else None.
        """
        try:
            credential = db.session.query(cls).filter_by(hubspot_portal_id=hubspot_portal_id).first()
            if credential:
                logger.debug("Found credential for Hubspot portal ID %d.", hubspot_portal_id)
            else:
                logger.info("No credential found for Hubspot portal ID %d.", hubspot_portal_id)
            return credential
        except SQLAlchemyError as e:
            logger.error("Failed to retrieve credential by hubspot_portal_id %d: %s",
                         hubspot_portal_id, str(e), exc_info=True)
            return None


    @classmethod
    def create(cls, hubspot_portal_id, hubspot_portal_domain, hubspot_user_id,
               hubspot_user_email, hubspot_scopes, hubspot_access_token,
               hubspot_refresh_token, hubspot_expires_in, **kwargs):
        """
        Create a new HubspotCredentials entry.

        Args:
            hubspot_portal_id: Unique identifier for the Hubspot portal.
            hubspot_portal_domain: Domain name associated with the Hubspot portal.
            hubspot_user_id: User ID of the Hubspot user.
            hubspot_user_email: Email address of the Hubspot user.
            hubspot_scopes: Scopes granted by the Hubspot OAuth.
            hubspot_access_token: OAuth access token for Hubspot API.
            hubspot_refresh_token: OAuth refresh token for Hubspot API.
            hubspot_expires_in: Token expiration time in seconds.

        Returns:
            The newly created HubspotCredentials object or None in case of an error.
        """
        try:
            new_credential = cls(
                hubspot_portal_id=hubspot_portal_id,
                hubspot_portal_domain=hubspot_portal_domain,
                hubspot_user_id=hubspot_user_id,
                hubspot_user_email=hubspot_user_email,
                hubspot_scopes=hubspot_scopes,
                hubspot_access_token=hubspot_access_token,
                hubspot_refresh_token=hubspot_refresh_token,
                hubspot_expires_in=hubspot_expires_in,
                **kwargs,
            )
            db.session.add(new_credential)
            db.session.commit()
            logger.info("Created new Hubspot credential with portal ID %d.", hubspot_portal_id)
            return new_credential
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Failed to create new credential: %s", str(e), exc_info=True)
            return None

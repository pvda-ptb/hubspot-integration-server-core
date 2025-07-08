from hubspot.utils.signature import Signature
from hubspot.exceptions import InvalidSignatureVersionError, InvalidSignatureTimestampError

from functools import wraps
import logging

from flask import request, abort


# Set up a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def validate_hubspot_signature(config: dict):
    """Decorator to validate HubSpot signatures on Flask routes.

    The decorator uses the Signature utility to ensure that incoming requests
    from HubSpot are legitimate by verifying the signature, method, URI, and
    timestamp provided in headers against the client secret.

    Args:
        config (HubspotIntegrationConfig): Configuration containing client secret.

    Raises:
        403 Forbidden: If the signature is invalid.
        400 Bad Request: If the signature version or timestamp is invalid.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract headers and request details
            signature_version = request.headers.get('X-HubSpot-Signature-Version')
            request_signature = request.headers.get('X-HubSpot-Signature')
            timestamp = request.headers.get("X-HubSpot-Request-Timestamp")
            request_method = request.method
            request_uri = request.full_path
            request_body = request.get_data(as_text=True)

            # Log the extracted request details for debugging
            logger.debug(f"Request Method: {request_method}, URI: {request_uri}, Body: {request_body}")

            try:
                # Validate the signature using Signature utility
                if not Signature.is_valid(
                    signature=request_signature,
                    client_secret=config['HUBSPOT_CLIENT_SECRET'],
                    request_body=request_body,
                    http_uri=request_uri,
                    http_method=request_method,
                    signature_version=signature_version,
                    timestamp=timestamp
                ):
                    logger.debug("Invalid signature received.")
                    abort(403, description="Invalid signature.")

            except (InvalidSignatureVersionError, InvalidSignatureTimestampError) as e:
                # Log error details for debugging
                logger.debug(f"Signature validation error: {str(e)}")
                abort(400, description=str(e))

            return f(*args, **kwargs)

        return decorated_function

    return decorator

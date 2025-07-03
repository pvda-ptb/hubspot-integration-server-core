from flask import request, render_template, redirect, url_for, current_app as app
from .helpers import default_oauth_process
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set logging level to debug

def oauth_callback():
    """
    Handle the OAuth callback by either displaying a custom form or
    processing the OAuth directly via a default method.
    """
    code = request.args.get('code')
    oauth_blueprint = app.blueprints['oauth']

    logger.debug("OAuth callback invoked with code: %s", code)

    if oauth_blueprint.custom_oauth_form:
        logger.debug("Rendering custom OAuth form.")
        return render_template(oauth_blueprint.custom_oauth_form, code=code)
    else:
        logger.debug("Processing OAuth using the default method.")
        return default_oauth_process(code, oauth_blueprint.oauth_server.api_client)

def process_oauth():
    """
    Process OAuth code and retrieve tokens, then handle these credentials.
    """
    code = request.form.get('code')
    oauth_blueprint = app.blueprints['oauth']
    logger.debug("Processing OAuth with code: %s", code)

    try:
        config = oauth_blueprint.oauth_server.config

        # Obtain OAuth Tokens
        tokens = oauth_blueprint.oauth_server.api_client.oauth.tokens_api.create(
            grant_type="authorization_code",
            redirect_uri=config.hubspot_oauth_redirect_url,
            client_id=config.hubspot_client_id,
            client_secret=config.hubspot_client_secret,
            code=code
        )

        # Fetch token details using the access token
        tokens_details = oauth_blueprint.oauth_server.api_client.oauth.access_tokens_api.get(tokens.access_token)

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

        form_data = request.form.to_dict()
        del form_data['code']

        # Process the tokens and additional form data
        oauth_blueprint.oauth_server.process_tokens(credentials_data, form_data)

        logger.debug("OAuth processing successful, redirecting to success page.")
        return redirect(url_for('.success'))

    except Exception as e:
        logger.error("Failed to process OAuth: %s", e)
        return "OAuth processing failed", 500

def success():
    """
    Indicate successful authentication.
    """
    return "Authentication successful", 200

# requests_app/awx_utils.py

import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def trigger_awx_job(server_request):
    """
    Triggers the specified AWX Job Template with server_request details.

    Args:
        server_request: The ServerRequest model instance.

    Returns:
        The AWX Job ID if successfully launched, otherwise None.
    """
    awx_url = settings.AWX_URL
    awx_token = settings.AWX_TOKEN
    template_id = settings.AWX_JOB_TEMPLATE_ID

    if not all([awx_url, awx_token, template_id]):
        logger.error("AWX settings (URL, Token, Template ID) are not fully configured.")
        return None

    # Ensure template_id is an integer if it came from env var
    try:
        template_id = int(template_id)
    except (ValueError, TypeError):
         logger.error(f"Invalid AWX_JOB_TEMPLATE_ID: {template_id}. Must be an integer.")
         return None

    launch_url = f"{awx_url.rstrip('/')}/api/v2/job_templates/{template_id}/launch/"
    headers = {
        'Authorization': f'Bearer {awx_token}',
        'Content-Type': 'application/json',
    }

    # Prepare extra_vars based on the request model
    # **IMPORTANT**: Adjust these keys to match EXACTLY what your
    #              Ansible playbook expects in `extra_vars`.
    extra_vars = {
        "target_fqdn": server_request.fqdn,
        "target_vlan": server_request.vlan,
        "target_site": server_request.site,
        "req_primary_contact": server_request.primary_contact,
        "req_secondary_contact": server_request.secondary_contact,
        "req_group_contact": server_request.group_contact,
        "req_notes": server_request.notes,
        "req_backup": server_request.backup_required,
        "req_monitoring": server_request.monitoring_required,
        "req_asap_number": server_request.asap_number,
        "request_portal_id": server_request.id # Useful for potential callbacks
    }

    payload = {
        "extra_vars": json.dumps(extra_vars)
        # Add other launch parameters if needed (e.g., inventory, limit)
        # "inventory": 1,
        # "limit": server_request.fqdn,
    }

    try:
        logger.info(f"Attempting to launch AWX Job Template {template_id} for request {server_request.id} ({server_request.fqdn})")
        # In development, you might want to disable SSL verification if AWX uses self-signed cert
        # For production with valid certs, set verify=True or remove the verify parameter
        response = requests.post(launch_url, headers=headers, json=payload, verify=False)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX, 5XX)

        job_data = response.json()
        job_id = job_data.get('job')

        if job_id:
            logger.info(f"Successfully launched AWX Job {job_id} for request {server_request.id}")
            return job_id
        else:
            logger.error(f"AWX job launch response did not contain a job ID. Response: {job_data}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error launching AWX job for request {server_request.id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"AWX Response Status Code: {e.response.status_code}")
            logger.error(f"AWX Response Body: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during AWX job launch for request {server_request.id}: {e}")
        return None

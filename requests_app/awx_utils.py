# requests_app/awx_utils.py
import requests
import json
import logging
from django.conf import settings
from .models import ServerRequest

logger = logging.getLogger(__name__)

def trigger_awx_job(server_request: ServerRequest):
    """
    Triggers the specified AWX Job Template with server_request details.
    Returns: The AWX Job ID if successfully launched, otherwise None.
    """
    awx_url = settings.AWX_URL
    awx_token = settings.AWX_TOKEN
    template_id = settings.AWX_JOB_TEMPLATE_ID

    if not all([awx_url, awx_token, template_id]):
        logger.error("AWX settings (URL, Token, Template ID) are not fully configured.")
        return None

    try:
        template_id = int(template_id)
    except (ValueError, TypeError):
         logger.error(f"Invalid AWX_JOB_TEMPLATE_ID: {template_id}. Must be an integer.")
         return None

    if not awx_url.startswith(('http://', 'https://')):
        awx_url = 'https://' + awx_url
    awx_url = awx_url.rstrip('/')

    launch_url = f"{awx_url}/api/v2/job_templates/{template_id}/launch/"
    headers = {
        'Authorization': f'Bearer {awx_token}',
        'Content-Type': 'application/json',
    }

    extra_vars = {
        "target_fqdn": server_request.fqdn,
        "target_vlan": server_request.vlan,
        "target_location": server_request.location,
        "req_primary_contact": server_request.primary_contact,
        "req_secondary_contact": server_request.secondary_contact,
        "req_group_contact": server_request.group_contact,
        "req_ticket_number": server_request.ticket_number,
        "req_notes": server_request.notes,
        "req_backup": server_request.backup_required,
        "req_monitoring": server_request.monitoring_required,
        "request_portal_id": server_request.id,
        "req_os_type": server_request.os_type,
        "req_cpu_cores": server_request.cpu_cores,
        "req_memory_gb": server_request.memory_gb,
        "req_os_disk_gb": server_request.os_disk_gb,
        "req_data_disk_gb": server_request.data_disk_gb, # Can be None
        "req_patching_group": server_request.patching_group,
        "req_user_ids": server_request.user_ids,
        "req_hypervisor_type": server_request.hypervisor_type,
    }

    # Filter out None values before sending to AWX if needed by playbook
    # extra_vars_filtered = {k: v for k, v in extra_vars.items() if v is not None}
    # Use extra_vars_filtered in json.dumps if needed

    payload = {
         "extra_vars": json.dumps(extra_vars) # Send original dict for now
    }

    verify_ssl = awx_url.startswith('https://')

    try:
        logger.info(f"Attempting to launch AWX Job Template {template_id} via {launch_url} for request {server_request.id} ({server_request.fqdn})")
        response = requests.post(launch_url, headers=headers, json=payload, verify=verify_ssl, timeout=30)
        response.raise_for_status()

        job_data = response.json()
        job_id = job_data.get('job')

        if job_id:
            logger.info(f"Successfully launched AWX Job {job_id} for request {server_request.id}")
            return job_id
        else:
            logger.error(f"AWX job launch response did not contain a job ID. Response Status: {response.status_code}, Body: {response.text}")
            return None
    except requests.exceptions.Timeout:
         logger.error(f"Timeout connecting to AWX ({launch_url}) for request {server_request.id}")
         return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error connecting to AWX ({launch_url}) for request {server_request.id}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error launching AWX job for request {server_request.id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"AWX Response Status Code: {e.response.status_code}")
            logger.error(f"AWX Response Body: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during AWX job launch for request {server_request.id}: {e}", exc_info=True)
        return None

import logging
from globus_sdk import TransferClient, GlobusAPIError
from django.contrib.auth.models import User

log = logging.getLogger(__name__)

from globus_portal_framework.gclients import load_transfer_client


def lookup_gcs_stuff(user: User):

    transfer_client: TransferClient = load_transfer_client(user)
    log.info('Looked up GCS Stuff')
    return {}


def create_acl(user: User, identity_id: str, endpoint_id: str, path: str, permissions: str):
    """ Create an ACL

    Keyword arguments:
        user -- Django User object
        identity_id -- Identity UUID for ACL rule
        endpoint_id -- Endpoint/collection UUID
        path -- Filesystem path (most end with a '/')
        permissions -- 'r' for read only, 'rw' for read-write
    """
    transfer_client: TransferClient = load_transfer_client(user)
    log.info('Created GCS ACL')

    # ACL paths must end with slash
    if path[-1] != "/":
        path = path + "/"

    rule_data = {
        "DATA_TYPE": "access",
        "principal_type": "identity",
        "principal": identity_id,
        "path": path,
        "permissions": permissions,
    }

    try:
        result = transfer_client.add_endpoint_acl_rule(endpoint_id, rule_data)
        rule_id = result["access_id"]
        return rule_id
    except GlobusAPIError as e:
        raise e.message

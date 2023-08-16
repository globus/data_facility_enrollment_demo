import logging
from globus_sdk import TransferClient, GlobusAPIError
from django.contrib.auth.models import User

log = logging.getLogger(__name__)

from globus_portal_framework.gclients import load_transfer_client


def lookup_guest_collections(user: User, keyword="arc_collection"):
    """Return a list of guest collections that contain the specified keyword
    Arguments:
        user -- Django User object
        keyword -- Only return guest collections matches the specified keyword
    """
    transfer_client: TransferClient = load_transfer_client(user)
    guest_collections = []
    endpoints = transfer_client.endpoint_manager_monitored_endpoints()
    for endpoint in endpoints:
        if (
            endpoint["entity_type"].endswith("guest_collection")
            and endpoint["keywords"]
            and keyword in endpoint["keywords"]
        ):
            guest_collections.append(endpoint)
    log.info(
        f"Found {len(guest_collections)} available guest collections for {user.username}"
    )
    return guest_collections


def get_available_mapped_collections():
    """
    Get a list of mapped collections which can be used my the app to create guest collections for the user.
    """
    return [
        {
            "uuid": "9da7942b-3fae-4ce9-b930-a335e41382cd",
            "name": "(Nick's collection) Mock Turbo Active Compute Storage",
            "tag": "arc_collection",
        },
    ]


def verify_valid_guest_collection():
    log.error("We currently do not check if a guest collection has the proper ACL")
    return False


def create_acl(
    user: User, identity_id: str, endpoint_id: str, path: str, permissions: str
):
    """Create an ACL

    Arguments:
        user -- Django User object
        identity_id -- Identity UUID for ACL rule
        endpoint_id -- Endpoint/collection UUID
        path -- Filesystem path (most end with a '/')
        permissions -- 'r' for read only, 'rw' for read-write
    """
    transfer_client: TransferClient = load_transfer_client(user)
    log.info("Created GCS ACL")

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
        raise RuntimeError(e.message)

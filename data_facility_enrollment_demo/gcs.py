from data_facility_enrollment_demo.exc import MissingKeyword
from globus_portal_framework.gclients import load_transfer_client
import logging
from globus_sdk import (
    AccessTokenAuthorizer,
    ConfidentialAppAuthClient,
    ClientCredentialsAuthorizer,
    GCSClient,
    GuestCollectionDocument,
    TransferClient,
    GlobusAPIError,
    UserCredentialDocument,
    scopes
)
from django.conf import settings
from django.contrib.auth.models import User

from globus_portal_framework.gclients import load_globus_access_token

log = logging.getLogger(__name__)


def lookup_guest_collections(user: User, keyword: str):
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


def verify_guest_collection_permissions(user: User, collection_id: str, group: str, permissions: str = 'rw'):
    """ Returns true if the guest collection has an ACL that matches parameters, or false otherwise
    Arguments:
       user -- Django User object
       collection_id -- Collection id to verify collection permissions
       group -- Group wich is being asserted access
       permissions -- 'rw' for read-write
    """
    transfer_client: TransferClient = load_transfer_client(user)

    acl_rules = transfer_client.endpoint_acl_list(collection_id)
    for acl_rule in acl_rules:
        if acl_rule['principal'] == group and acl_rule['permissions'] == permissions:
            return True

    log.warning(f'No ACL rule exists for group {group}')
    rule_data = {
        "DATA_TYPE": "access",
        "principal_type": "group",
        "principal": group,
        "path": "/",
        "permissions": "rw",
    }
    transfer_client.add_endpoint_acl_rule(collection_id, rule_data)
    log.info(f'Added {group} to collection {collection_id}...')
    return True


def verify_guest_collection_keywords(user: User, collection_id: str, keyword):
    """
    Ensure guest collection contains keywords. It shouldn't be possible to fail here, since only collections
    returned in the get function above select for collections containing the required keywords
    """
    transfer_client: TransferClient = load_transfer_client(user)
    data = transfer_client.get_endpoint(collection_id)

    if not data['keywords'] or keyword not in data['keywords']:
        raise MissingKeyword('Missing Keyword on collection')


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


def create_guest_collection(
        display_name: str,
        endpoint_hostname: str,
        endpoint_id: str,
        mapped_collection_id: str,
        storage_gateway_id: str,
        user: User):
    # constants
    endpoint_hostname = endpoint_hostname
    endpoint_id = endpoint_id
    mapped_collection_id = mapped_collection_id
    storage_gateway_id = storage_gateway_id

    # client credentials
    # This client identity must have the needed permissions to create a guest
    # collection on the mapped collection, and a valid mapping to a local account
    # on the storage gateway that matches the local_username
    # If using user tokens, the user must be the one with the correct permissions
    # and identity mapping.
    local_username = user.username.split("@")[0]

    # The scope the client will need, note that primary scope is for the endpoint,
    # but it has a dependency on the mapped collection's data_access scope
    scope = scopes.GCSEndpointScopeBuilder(
        endpoint_id).make_mutable("manage_collections")
    scope.add_dependency(scopes.GCSCollectionScopeBuilder(
        mapped_collection_id).data_access)

    # Build a GCSClient to act as the client by using a ClientCredentialsAuthorizor
    authorizer = AccessTokenAuthorizer(
        load_globus_access_token(user, endpoint_id))
    client = GCSClient(endpoint_hostname, authorizer=authorizer)

    # The identity creating the guest collection must have a user credential on
    # the mapped collection.
    # Note that this call is connector specific. Most connectors will require
    # connector specific policies to be passed here, but POSIX does not.
    credential_document = UserCredentialDocument(
        storage_gateway_id=storage_gateway_id,
        identity_id=user.social_auth.get(provider='globus').uid,
        username=local_username,
    )

    try:
        client.create_user_credential(credential_document)
    except Exception:
        pass

    # Create the collection
    collection_document = GuestCollectionDocument(
        public="True",
        collection_base_path="/",
        display_name=display_name,
        keywords="arc_collection",
        mapped_collection_id=mapped_collection_id,
    )
    response = client.create_collection(collection_document)

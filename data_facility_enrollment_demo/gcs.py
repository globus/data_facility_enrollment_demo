import logging
from globus_sdk import TransferClient
from django.contrib.auth.models import User

log = logging.getLogger(__name__)

from globus_portal_framework.gclients import load_transfer_client


def lookup_gcs_stuff(user: User):

    transfer_client: TransferClient = load_transfer_client(user)
    log.info('Looked up GCS Stuff')
    return {}


def create_acl(user: User):
    transfer_client: TransferClient = load_transfer_client(user)
    log.info('Created GCS ACL')

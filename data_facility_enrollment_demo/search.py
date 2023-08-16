import logging
from globus_sdk import SearchClient
from django.contrib.auth.models import User

log = logging.getLogger(__name__)

from globus_portal_framework.gclients import load_search_client


def create_search_record(user: User):

    search_client = load_search_client(user)

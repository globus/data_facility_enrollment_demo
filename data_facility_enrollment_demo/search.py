import logging
from globus_sdk import SearchClient
from data_facility_enrollment_demo.searchwriter import ConfidentialSearchClient
from django.contrib.auth.models import User

log = logging.getLogger(__name__)



def create_search_record(projectID, collectionID, user: User):

    search_client = ConfidentialSearchClient()
    search_client.write_to_index(projectID, collectionID, user.username)

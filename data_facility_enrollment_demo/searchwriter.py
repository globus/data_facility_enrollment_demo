import globus_sdk
import time
from django.conf import settings

# Put SEARCH_INDEX_UUID in settings.
# SEARCH_INDEX_UUID = '8c47de5e-a969-4912-abd5-c29130ae526e'


class ConfidentialSearchClient:
    """
    Class for interacting with the search index
    """

    def __init__(self, auth_client: globus_sdk.AuthClient = None, search_client: globus_sdk.SearchClient = None):

        self.auth_client = (
            globus_sdk.ConfidentialAppAuthClient(
                settings.SOCIAL_AUTH_GLOBUS_KEY,
                settings.SOCIAL_AUTH_GLOBUS_SECRET) 
        )

        # Create a Globus Search API client using the client credentials of the lambda function
        scopes = (globus_sdk.scopes.SearchScopes.all)
        self.cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(
            self.auth_client, scopes)
        self.search_client = (
            globus_sdk.SearchClient(
                authorizer=self.cc_authorizer) if not search_client else search_client
        )

    def write_to_index(self, project_id, collection_uuid, uniquename):

        gmeta_ingest = {
            "ingest_type": "GMetaEntry",
            "ingest_data": {
                "subject": project_id + ":" + collection_uuid,
                "mimetype": "application/json",
                "visible_to": [
                    "public"
                ],
                "id": project_id + ":" + collection_uuid,
                "content": {
                    "projectID": project_id,
                    "collectionID": collection_uuid,
                    "timestamp": time.time()
                }
            }
        }

        # Ingest the document file into Globus Search
        res = self.search_client.ingest(settings.SEARCH_INDEX_UUID, gmeta_ingest)


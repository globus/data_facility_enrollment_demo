import json
from django.conf import settings
import logging

log = logging.getLogger(__name__)


class ARCClient(object):
    """This is a mock API for accessing ARC specific projects and storage for a given user"""

    def __init__(self, user):
        log.info(f"Authorized fake ARC user {user.username}")

    @staticmethod
    def load_json(filename):
        with open(filename) as f:
            return json.load(f)

    def get_projects(self):
        return self.load_json(settings.ARC_PROJECT_FILE)

    def get_storage(self):
        return self.load_json(settings.ARC_STORAGE_FILE)

import frappe
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import HACKATHON_TEAM_MEMBER
from fossunited.tests.utils import (
    insert_test_hackathon,
    insert_test_hackathon_participant,
    insert_test_hackathon_team,
)


class TestFOSSHackathonTeam(IntegrationTestCase):
    def setUp(self):
        self.hackathon = insert_test_hackathon(is_team_mandatory=True, max_team_members=3)

        self.team = insert_test_hackathon_team(hackathon=self.hackathon)

        self.participants = []
        for _ in range(4):  # since max_team_size is 2, we need 3 participants to test the code
            participant = insert_test_hackathon_participant(hackathon_id=self.hackathon.name)
            self.participants.append(participant)

    def tearDown(self):
        frappe.set_user("Administrator")
        self.team.delete(force=True)
        for participant in self.participants:
            participant.delete(force=True)
        self.hackathon.delete(force=True)

    def test_add_member_to_team(self):
        # Given a hackathon with a defined max_team_members size
        # When the max number of participants are added to that team
        participant_ids = []
        for _ in range(self.hackathon.max_team_members):
            participant_ids.append(self.participants[_].name)
            self.team.append("members", {"member": self.participants[_].name})
        self.team.save()

        # Then it should add those members to the team without any error
        self.assertEqual(len(self.team.members), self.hackathon.max_team_members)

        # Get participant ids of team members of self.team, those should match the
        # IDs of participants that were meant to be added to the team
        members_emails = frappe.get_all(
            HACKATHON_TEAM_MEMBER, {"parent": self.team.name}, pluck="member"
        )
        self.assertEqual(members_emails.sort(), participant_ids.sort())

    def test_add_member_exceeding_max_size(self):
        # Given a hackathon with a defined max number of team members
        # When more than max no. of members are tried to be added to a team
        for _ in range(self.hackathon.max_team_members + 1):
            self.team.append("members", {"member": self.participants[_].name})
        # Then a validation error should be raised.
        self.assertRaises(frappe.exceptions.ValidationError, self.team.save)

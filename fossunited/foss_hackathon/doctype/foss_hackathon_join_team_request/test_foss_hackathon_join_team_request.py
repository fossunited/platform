import frappe
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import HACKATHON_TEAM_MEMBER
from fossunited.tests.utils import (
    insert_test_hackathon,
    insert_test_hackathon_join_request,
    insert_test_hackathon_participant,
    insert_test_hackathon_team,
)


class TestFOSSHackathonJoinTeamRequest(IntegrationTestCase):
    def setUp(self):
        self.hackathon = insert_test_hackathon()

        self.member1 = "test1@example.com"
        participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name, user=self.member1, email=self.member1
        )

        self.team = insert_test_hackathon_team(hackathon=self.hackathon)
        # add member 1 to self.team
        self.team.append(
            "members",
            {
                "member": participant.name,
                "full_name": participant.full_name,
                "email": participant.email,
            },
        )
        self.team.save()

        self.reciever_email = "test4@example.com"
        self.reciever_participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name, user=self.reciever_email, email=self.reciever_email
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        self.hackathon.delete(force=True)
        self.team.delete(force=True)

    def test_sender_is_team_member(self):
        # Given a team member
        frappe.set_user(self.member1)
        # when the user tries to create a join request
        # then it should be created without any problem
        insert_test_hackathon_join_request(
            hackathon_id=self.hackathon.name,
            team_id=self.team.name,
            requested_by=self.member1,
            reciever_email=self.reciever_email,
        )

        # when a non member tries to send request
        non_member_user = "test3@example.com"
        frappe.set_user(non_member_user)
        # then it should throw a frappe.ValidationError
        with self.assertRaises(frappe.ValidationError):
            insert_test_hackathon_join_request(
                hackathon_id=self.hackathon.name,
                team_id=self.team.name,
                requested_by=non_member_user,
                reciever_email=self.reciever_email,
            )

    def test_add_to_team(self):
        # Given a join request
        frappe.set_user(self.member1)
        request = insert_test_hackathon_join_request(
            hackathon_id=self.hackathon.name,
            team_id=self.team.name,
            requested_by=self.member1,
            reciever_email=self.reciever_email,
        )

        self.assertFalse(
            frappe.db.exists(
                HACKATHON_TEAM_MEMBER,
                {"parent": request.team, "member": self.reciever_participant.name},
            )
        )

        # When the request is accepted
        frappe.set_user(self.reciever_email)
        request.status = "Accepted"
        request.save()

        # Then a team member should be added to the request's team
        self.assertTrue(
            frappe.db.exists(
                HACKATHON_TEAM_MEMBER,
                {"parent": request.team, "member": self.reciever_participant.name},
            )
        )

    def test_reject_other_responses(self):
        team1 = self.team
        team1_member = self.member1
        team2 = insert_test_hackathon_team(hackathon=self.hackathon)
        team2_member = "test2@example.com"
        team2_participant = insert_test_hackathon_participant(
            hackathon_id=self.hackathon.name, user=team2_member, email=team2_member
        )
        team2.append(
            "members",
            {
                "member": team2_participant.name,
                "full_name": team2_participant.full_name,
                "email": team2_participant.email,
            },
        )
        team2.save()
        team2.reload()

        request_reciever = self.reciever_email

        # As member of team 1
        frappe.set_user(team1_member)
        # Create a join request for request_reciever
        request1 = insert_test_hackathon_join_request(
            hackathon_id=self.hackathon.name,
            team_id=team1.name,
            requested_by=frappe.session.user,
            reciever_email=request_reciever,
        )
        self.assertEqual(request1.status, "Pending")

        # As member of team 2
        frappe.set_user(team2_member)
        # create a join request for same request_reciever
        request2 = insert_test_hackathon_join_request(
            hackathon_id=self.hackathon.name,
            team_id=team2.name,
            requested_by=frappe.session.user,
            reciever_email=request_reciever,
        )
        self.assertEqual(request2.status, "Pending")

        # if the first request is accepted by the reciever
        frappe.set_user(request_reciever)
        request1.status = "Accepted"
        request1.save()
        request1.reload()

        self.assertEqual(request1.status, "Accepted")

        # Then the second request should be automatically rejected
        request2.reload()
        self.assertEqual(request2.status, "Rejected")

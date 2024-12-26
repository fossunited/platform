# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
from datetime import datetime

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import CHAPTER, HACKATHON_PROJECT, PROPOSAL, USER_PROFILE

no_cache = 1

BASE_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


class FOSSHackathon(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.chapters.doctype.foss_event_community_partner.foss_event_community_partner import (  # noqa: E501
            FOSSEventCommunityPartner,
        )
        from fossunited.fossunited.doctype.foss_event_schedule.foss_event_schedule import (
            FOSSEventSchedule,
        )
        from fossunited.fossunited.doctype.foss_event_sponsor.foss_event_sponsor import (
            FOSSEventSponsor,
        )

        chapter: DF.Link | None
        community_partners: DF.Table[FOSSEventCommunityPartner]
        contribution_coming_soon_description: DF.SmallText | None
        contribution_project_guidelines: DF.MarkdownEditor | None
        enable_oss_contributon_projects: DF.Check
        end_date: DF.Datetime
        external_website_url: DF.Data | None
        hackathon_banner: DF.AttachImage | None
        hackathon_description: DF.TextEditor
        hackathon_faq: DF.TextEditor | None
        hackathon_logo: DF.AttachImage | None
        hackathon_name: DF.Data
        hackathon_rules: DF.TextEditor | None
        hackathon_type: DF.Literal["", "Remote", "In-person", "Hybrid"]  # noqa: F722, F821
        has_external_website: DF.Check
        has_localhosts: DF.Check
        has_partner_projects: DF.Check
        is_contribution_project_coming_soon: DF.Check
        is_published: DF.Check
        is_registration_live: DF.Check
        is_team_mandatory: DF.Check
        max_team_members: DF.Int
        only_show_logo: DF.Check
        partner_project_guidelines: DF.MarkdownEditor | None
        permalink: DF.Data | None
        registration_description: DF.TextEditor | None
        route: DF.Data | None
        schedule: DF.Table[FOSSEventSchedule]
        show_schedule_tab: DF.Check
        sponsor_list: DF.Table[FOSSEventSponsor]
        start_date: DF.Datetime
    # end: auto-generated types

    def before_save(self):
        self.set_route()

    def set_route(self):
        if self.permalink:
            self.route = f"hack/{self.permalink}"
        else:
            self.route = f'hack/{self.hackathon_name.lower().replace(" ", "-")}'

    def get_context(self, context):
        if self.chapter:
            context.chapter = frappe.get_doc(CHAPTER, self.chapter)

        context.nav_items = self.get_nav_items()
        context.sponsors_dict = self.get_sponsors()
        context.tag_icon = {
            "Remote": "world",
            "In-person": "building",
            "Hybrid": "world",
        }

        context.schedule_dict = self.get_schedule_dict()
        context.recent_projects = frappe.get_all(
            HACKATHON_PROJECT,
            filters={"hackathon": self.name},
            fields=["*"],
        )

    def get_nav_items(self):
        nav_items = ["information", "submissions"]
        if self.show_schedule_tab:
            nav_items.append("schedule")

        return nav_items

    def get_sponsors(self):
        sponsors_dict = {}
        for sponsor in self.sponsor_list:
            if sponsor.sponsorship_tier not in sponsors_dict:
                sponsors_dict[sponsor.sponsorship_tier] = []
            sponsors_dict[sponsor.sponsorship_tier].append(sponsor)
        return sponsors_dict

    def get_schedule_dict(self):
        schedule_dict = {}
        for schedule in self.schedule:
            date = schedule.scheduled_date.strftime("%-d %B")
            if date not in schedule_dict:
                schedule_dict[date] = []
            get_speakers(schedule)
            if schedule.start_time:
                schedule.start_time = BASE_DATE + schedule.start_time
            if schedule.end_time:
                schedule.end_time = BASE_DATE + schedule.end_time
            schedule_dict[date].append(schedule)

        schedule_dict["days"] = list(schedule_dict.keys())
        return schedule_dict


def get_speakers(schedule):
    if not schedule.linked_cfp:
        schedule.no_speaker = True
        return

    cfp = frappe.get_doc(PROPOSAL, schedule.linked_cfp)
    user = frappe.get_doc(USER_PROFILE, {"email": cfp.submitted_by})
    schedule.cfp_route = cfp.route
    schedule.speaker_route = user.route
    schedule.speaker_full_name = user.full_name
    schedule.speaker_designation_company = cfp.designation + " at " + cfp.organization

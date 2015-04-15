from __future__ import absolute_import, unicode_literals

from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from mock import patch
from upartners.cases.models import Case, ACTION_OPEN, ACTION_NOTE, ACTION_CLOSE, ACTION_REOPEN, ACTION_REASSIGN
from upartners.test import UPartnersTest


class CaseTest(UPartnersTest):
    def test_lifecyle(self):
        d0 = datetime(2014, 1, 2, 6, 0, tzinfo=timezone.utc)
        d1 = datetime(2014, 1, 2, 7, 0, tzinfo=timezone.utc)
        d2 = datetime(2014, 1, 2, 8, 0, tzinfo=timezone.utc)
        d3 = datetime(2014, 1, 2, 9, 0, tzinfo=timezone.utc)
        d4 = datetime(2014, 1, 2, 10, 0, tzinfo=timezone.utc)
        d5 = datetime(2014, 1, 2, 11, 0, tzinfo=timezone.utc)
        d6 = datetime(2014, 1, 2, 12, 0, tzinfo=timezone.utc)

        with patch.object(timezone, 'now', return_value=d1):
            # MOH user assigns to self
            case = Case.open(self.unicef, self.user1, [self.aids], self.moh, 'C-001', 123, d0)

        self.assertEqual(case.org, self.unicef)
        self.assertEqual(set(case.labels.all()), {self.aids})
        self.assertEqual(case.assignee, self.moh)
        self.assertEqual(case.contact_uuid, 'C-001')
        self.assertEqual(case.opened_on, d1)
        self.assertIsNone(case.closed_on)

        actions = case.actions.all()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action, ACTION_OPEN)
        self.assertEqual(actions[0].created_by, self.user1)
        self.assertEqual(actions[0].created_on, d1)
        self.assertEqual(actions[0].assignee, self.moh)

        with patch.object(timezone, 'now', return_value=d2):
            # other user in MOH adds a note
            case.note(self.user2, "Interesting")

        actions = case.actions.all()
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[1].action, ACTION_NOTE)
        self.assertEqual(actions[1].created_by, self.user2)
        self.assertEqual(actions[1].created_on, d2)
        self.assertEqual(actions[1].note, "Interesting")

        # user from other partner org can't close case
        self.assertRaises(PermissionDenied, case.close, self.user3)

        with patch.object(timezone, 'now', return_value=d3):
            # first user closes the case
            case.close(self.user1)

        self.assertEqual(case.opened_on, d1)
        self.assertEqual(case.closed_on, d3)

        actions = case.actions.all()
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[2].action, ACTION_CLOSE)
        self.assertEqual(actions[2].created_by, self.user1)
        self.assertEqual(actions[2].created_on, d3)

        with patch.object(timezone, 'now', return_value=d4):
            # but second user re-opens it
            case.reopen(self.user2)

        self.assertEqual(case.opened_on, d1)  # unchanged
        self.assertIsNone(case.closed_on)

        actions = case.actions.all()
        self.assertEqual(len(actions), 4)
        self.assertEqual(actions[3].action, ACTION_REOPEN)
        self.assertEqual(actions[3].created_by, self.user2)
        self.assertEqual(actions[3].created_on, d4)

        with patch.object(timezone, 'now', return_value=d5):
            # and re-assigns it to different partner
            case.reassign(self.user2, self.who)

        self.assertEqual(case.assignee, self.who)

        actions = case.actions.all()
        self.assertEqual(len(actions), 5)
        self.assertEqual(actions[4].action, ACTION_REASSIGN)
        self.assertEqual(actions[4].created_by, self.user2)
        self.assertEqual(actions[4].created_on, d5)
        self.assertEqual(actions[4].assignee, self.who)

        with patch.object(timezone, 'now', return_value=d6):
            # user from that partner org closes it again
            case.close(self.user3)

        self.assertEqual(case.opened_on, d1)
        self.assertEqual(case.closed_on, d6)

        actions = case.actions.all()
        self.assertEqual(len(actions), 6)
        self.assertEqual(actions[5].action, ACTION_CLOSE)
        self.assertEqual(actions[5].created_by, self.user3)
        self.assertEqual(actions[5].created_on, d6)
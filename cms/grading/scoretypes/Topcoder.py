#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2012 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2012 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2014 Khanh Do Ngoc <dongockhanh1997@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from cms.grading.ScoreType import ScoreTypeACM
from cmscommon.datetime import make_timestamp


class Topcoder(ScoreTypeACM):
    """The score of a submission is the integer parameter
    if it is accepted or 0 otherwise.

    """

    def get_time(self, submission_result):
        """ Returns (float, float): (Time to code solution, Contest length)

        """
        submission = submission_result.submission
        user = submission.user
        contest = user.contest
        submission_time = make_timestamp(submission.timestamp)
        coding_time = total_time = 0.0
        if contest.per_user_time is not None:
            starting_time = make_timestamp(user.starting_time)
            coding_time = submission_time - starting_time
            total_time = contest.per_user_time.total_seconds()
        else:
            starting_time = make_timestamp(contest.start)
            ending_time = make_timestamp(contest.stop)
            coding_time = submission_time - starting_time
            total_time = ending_time - starting_time
        return coding_time, total_time

    def previous_submission_count(self, submission_result):
        """ Return (int): the number of previous submission
        which compilation was succeeded.

        """
        submission = submission_result.submission
        user = submission.user
        dataset = submission_result.dataset
        submission_time = make_timestamp(submission.timestamp)
        previous_submission = 0
        for other in user.submissions:
            if other.task_id == submission.task_id and \
                    make_timestamp(other.timestamp) < submission_time:
                while not other.get_result_or_create(dataset).compiled():
                    pass
                if other.get_result_or_create(dataset).compilation_succeeded():
                    previous_submission += 1
        return previous_submission

    def compute_score(self, submission_result):
        """ Compute the score of a submission.

        """
        score, testcases, public_score, public_testcases, tmp = \
            self.pre_compute_score(submission_result)
        coding_time, total_time = self.get_time(submission_result)
        previous_submision = self.previous_submission_count(submission_result)
        multipler = 0.3 + 0.7 * (total_time ** 2) \
            / (10 * (coding_time ** 2) + (total_time ** 2))
        max_score = self.parameters
        penalty = max_score / 10.0 * previous_submision
        min_score = max_score * 0.3
        if score > 0:
            score = score * max_score * multipler - penalty
            score = max(score, min_score)
        if public_score > 0:
            public_score = public_score * max_score * multipler - penalty
            public_score = max(public_score, min_score)
        return score, testcases, public_score, public_testcases, tmp

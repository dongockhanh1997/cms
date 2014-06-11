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


# Dummy function to mark translatable string.
def N_(message):
    return message


class Topcoder(ScoreTypeACM):
    """The score of a submission is the integer parameter
    if it is accepted or 0 otherwise.

    """
    def compute_score(self, submission_result):
        """ Compute the score of a submission.

        """
        score, testcases, public_score, public_testcases, tmp = \
            self.pre_compute_score(submission_result)
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
        multipler = 0.3 + 0.7 * (total_time ** 2) \
            / (10 * (coding_time ** 2) + (total_time ** 2))
        score *= self.parameters * multipler
        public_score *= self.parameters * multipler
        return score, testcases, public_score, public_testcases, tmp

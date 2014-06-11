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

from cms.grading.ScoreType import ScoreTypeGroup


# Dummy function to mark translatable string.
def N_(message):
    return message


class SmartGroupMin(ScoreTypeGroup):
    """The score of a submission is the sum of the product of the
    minimum of the ranges with the multiplier of that range
    and its depencency.

    Parameters are [[m, t, f, d], ... ] (see ScoreTypeGroup).
    f (bool, optional): Whether we will continue evaluating this subtask
        even when a testcase or one of its dependent subtasks has failed.
    d ([int], optional): The result of this subtask depend on the results
        of the subtasks in d. A subtask can depend on a subtask with lower
        index only. Invalid dependency will be ignored.

    """

    def get_public_outcome(self, outcome, parameter):
        """See ScoreTypeGroup."""
        if outcome <= 0.0:
            return N_("Not correct")
        elif outcome >= 1.0:
            return N_("Correct")
        else:
            return N_("Partially correct")

    def reduce(self, outcomes, parameter):
        """See ScoreTypeGroup."""
        return min(outcomes)

    def get_subtask(self, codename):
        """Return the subtask contain the codename testcase.

        codename (string): The testcase's codename.

        return (int): The subtask contain this testcase.

        """
        indices = sorted(self.public_testcases.keys())
        current = 0
        for i, parameters in enumerate(self.parameters):
            next_ = current + parameters[1]
            for test in xrange(current, next_):
                if indices[test] == codename:
                    return i
            current = next_
        return None

    def can_skip(self, codename, outcomes):
        """See ScoreTypeGroup."""
        indices = sorted(self.public_testcases.keys())
        subtask_outcomes = []
        current = 0
        for i, parameters in enumerate(self.parameters):
            next_ = current + parameters[1]
            st_outcome = 1.0
            for test in indices[current:next_]:
                if outcomes[test] is not None:
                    st_outcome = min(st_outcome, float(outcomes[test]))
            subtask_outcomes.append(st_outcome)
            current = next_
        subtask = self.get_subtask(codename)
        parameters = self.parameters[subtask]
        full_judge = len(parameters) > 2 and parameters[2]
        max_outcome = subtask_outcomes[subtask]
        if len(parameters) > 3:
            max_outcome = min(max_outcome, *(subtask_outcomes[x]
                              for x in parameters[3] if x < subtask))
        return not full_judge and max_outcome <= 0.0

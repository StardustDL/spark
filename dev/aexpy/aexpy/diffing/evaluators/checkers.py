#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Original repository: https://github.com/StardustDL/aexpy
# Copyright 2022 StardustDL <stardustdl@163.com>
#

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Callable

from aexpy.models.difference import BreakingRank

from aexpy.models import ApiDescription, ApiDifference, DiffEntry


class EvalRule:
    """
    A rule (evaluator) generating DiffEntry(s).

    checker: def checker(entry, difference) -> list[DiffEntry]: pass
    """

    def __init__(self, kind: "str" = "", checker: "Callable[[DiffEntry, ApiDifference, ApiDescription, ApiDescription], None] | None" = None) -> None:
        if checker is None:
            def tchecker(a: Any, b: Any, old: Any, new: Any):
                pass
            checker = tchecker
        self.checker: "Callable[[DiffEntry, ApiDifference, ApiDescription, ApiDescription], None]" = checker
        self.kind = kind

    def forkind(self, kind: "str"):
        """Set kind."""

        self.kind = kind
        return self

    def __call__(self, entry: "DiffEntry", diff: "ApiDifference", old: "ApiDescription", new: "ApiDescription") -> None:
        if self.kind and entry.kind != self.kind:
            return
        return self.checker(entry, diff, old, new)


@dataclass
class EvalRuleCollection:
    """Collection for rule evaluators."""

    rules: "list[EvalRule]" = field(default_factory=list)

    def rule(self, rule: "EvalRule"):
        self.rules.append(rule)
        return rule


def evalrule(checker: "Callable[[DiffEntry, ApiDifference, ApiDescription, ApiDescription], None]") -> "EvalRule":
    """Create a rule evaluator on a function."""

    return EvalRule(checker.__name__, checker)


def forallkinds(rule: "EvalRule") -> "EvalRule":
    """Create a rule evaluator for all kinds of DiffEntry."""

    return rule.forkind("")


def forkind(kind: str):
    """Create a rule evaluator for a kind of DiffEntry."""

    def decorator(rule: "EvalRule") -> "EvalRule":
        return rule.forkind(kind)

    return decorator


def rankAt(kind: str, rank: "BreakingRank", privateRank: "BreakingRank | None" = None):
    """Create a rule evaluator that ranks a kind of DiffEntry."""

    def checker(entry: "DiffEntry", diff: "ApiDifference", old: "ApiDescription", new: "ApiDescription") -> "None":
        eold = entry.old
        enew = entry.new
        if (eold and eold.private) or (enew and enew.private):
            entry.rank = privateRank if privateRank is not None else rank
        else:
            entry.rank = rank

    return EvalRule(kind, checker)

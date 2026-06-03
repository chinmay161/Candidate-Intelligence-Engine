"""Deterministic concern detection for candidate recommendations."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from jd_parser.jd_models import JDAnalysis
from ranking.contribution_tracker import feature_group
from ranking.match_models import CandidateMatch, MatchPenalty
from reasoning.reasoning_models import CandidateConcern, ReasoningEvidence


class ConcernDetector:
    """Identify grounded weaknesses and risks from penalties and missing signals."""

    FEATURE_CONCERNS: dict[str, str] = {
        "honeypot_score": "suspicious-profile risk",
        "services_only_penalty": "consulting-heavy or services-only career signal",
        "research_only_phd_penalty": "research-heavy profile with limited production support",
        "management_only_recent_penalty": "recent role appears less hands-on",
        "framework_demo_penalty_text": "demo-only framework language",
        "job_hop_title_chaser_penalty": "short-tenure progression risk",
        "nontech_role_penalty": "non-technical current-role signal",
        "ai_keyword_stuffing_penalty": "AI keyword density is not fully supported by role evidence",
        "notice_period_score": "longer-than-average notice period",
        "days_since_active_score": "inactive profile signal",
    }

    def detect(
        self,
        analysis: JDAnalysis,
        match: CandidateMatch,
        candidate: CandidateFeatureRecord,
    ) -> list[CandidateConcern]:
        concerns: list[CandidateConcern] = []

        missing_required = tuple(item for item in match.missing_requirements if item.startswith("required_skill:"))
        if missing_required:
            concerns.append(self._missing_requirement_concern(missing_required, "required"))

        for penalty in sorted(match.penalties, key=lambda item: (-item.value, item.feature, item.reason)):
            concerns.append(self._from_penalty(candidate, penalty))

        missing_preferred = tuple(item for item in match.missing_requirements if item.startswith("preferred_skill:"))
        if missing_preferred:
            concerns.append(self._missing_requirement_concern(missing_preferred, "preferred"))

        production = float(candidate.semantic_features.get("production_ir_evidence_score", 0.0))
        has_production_evidence = bool(candidate.evidence.get("production_ir_evidence_score"))
        requires_production = any(
            "production" in skill.canonical_name or "ranking" in skill.canonical_name
            for skill in analysis.required_skills + analysis.preferred_skills
        ) or "production" in analysis.job_description.raw_text.lower()
        if requires_production and production < 0.35 and not has_production_evidence:
            concerns.append(
                CandidateConcern(
                    category="production_evidence",
                    description="limited production retrieval or ranking evidence",
                    severity="medium",
                    supporting_evidence=(
                        ReasoningEvidence(
                            feature="production_ir_evidence_score",
                            group="semantic",
                            description="low production evidence score",
                            contribution=0.0,
                            raw_value=production,
                            snippets=(f"production_ir_evidence_score={production:.2f}",),
                            source="candidate_feature",
                        ),
                    ),
                )
            )

        return self._dedupe(concerns)[:5]

    def _from_penalty(self, candidate: CandidateFeatureRecord, penalty: MatchPenalty) -> CandidateConcern:
        raw_value, group = self._candidate_value(candidate, penalty.feature)
        snippets = tuple(candidate.evidence.get(penalty.feature)) or (penalty.reason,)
        description = self.FEATURE_CONCERNS.get(penalty.feature, penalty.reason)
        return CandidateConcern(
            category=penalty.feature or "penalty",
            description=description,
            severity=penalty.severity,
            supporting_evidence=(
                ReasoningEvidence(
                    feature=penalty.feature or "penalty",
                    group=group or "penalty",
                    description=penalty.reason,
                    contribution=-abs(penalty.value),
                    raw_value=raw_value,
                    snippets=snippets[:2],
                    source="match_penalty",
                ),
            ),
        )

    def _missing_requirement_concern(self, missing: tuple[str, ...], importance: str) -> CandidateConcern:
        cleaned = tuple(item.split(":", 1)[1].replace("_", " ") for item in missing[:3])
        description = f"missing {importance} JD requirement" if len(cleaned) == 1 else f"missing {importance} JD requirements"
        severity = "medium" if importance == "required" else "low"
        return CandidateConcern(
            category=f"missing_{importance}",
            description=f"{description}: {', '.join(cleaned)}",
            severity=severity,
            supporting_evidence=(
                ReasoningEvidence(
                    feature=f"missing_{importance}_requirements",
                    group="requirements",
                    description=description,
                    contribution=0.0,
                    raw_value=float(len(missing)),
                    snippets=missing[:5],
                    source="candidate_match",
                ),
            ),
        )

    def _candidate_value(self, candidate: CandidateFeatureRecord, feature: str) -> tuple[float, str]:
        for group in ("semantic", "experience", "skill", "behavioral", "career", "education", "logistics", "anomaly"):
            values = feature_group(candidate, group)
            if feature in values:
                return float(values[feature]), group
        return 0.0, ""

    def _dedupe(self, concerns: list[CandidateConcern]) -> list[CandidateConcern]:
        seen: set[str] = set()
        deduped: list[CandidateConcern] = []
        for concern in concerns:
            if concern.category in seen:
                continue
            seen.add(concern.category)
            deduped.append(concern)
        return deduped

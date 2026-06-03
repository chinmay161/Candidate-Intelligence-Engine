from __future__ import annotations

import unittest

from ranking.candidate_scorer import CandidateScorer
from ranking_fixtures import candidate_record, retrieval_jd
from reasoning.reasoning_generator import ReasoningGenerator


class ReasoningTop100StressTests(unittest.TestCase):
    def test_top100_stress_metrics(self) -> None:
        analysis = retrieval_jd()
        scorer = CandidateScorer()
        generator = ReasoningGenerator()

        candidates = []
        for i in range(100):
            # Systematically vary fit between 0.3 and 1.0
            fit = 0.3 + (i % 8) * 0.1

            # Systematically vary penalty: active for every 4th candidate
            penalty = 1.0 if (i % 4 == 0) else 0.0

            # Systematically vary notice period: low notice period score (high notice duration) for every 5th candidate
            notice_score = 0.2 if (i % 5 == 0) else 1.0

            cand_id = f"CAND_{i}"
            cand = candidate_record(cand_id, fit=fit, penalty=penalty, notice_score=notice_score)

            # Bit-based feature activation to guarantee diverse combinations of strengths
            # 1. production
            if i & 1:
                cand.semantic_features["production_ir_evidence_score"] = 0.85
                cand.evidence.by_feature["production_ir_evidence_score"] = ["Built production retrieval systems."]
            else:
                cand.semantic_features["production_ir_evidence_score"] = 0.10
                if "production_ir_evidence_score" in cand.evidence.by_feature:
                    del cand.evidence.by_feature["production_ir_evidence_score"]

            # 2. evaluation
            if i & 2:
                cand.skill_features["ranking_eval_phrase_score"] = 0.80
                cand.evidence.by_feature["ranking_eval_phrase_score"] = ["Measured search quality using NDCG and MAP."]
            else:
                cand.skill_features["ranking_eval_phrase_score"] = 0.10
                if "ranking_eval_phrase_score" in cand.evidence.by_feature:
                    del cand.evidence.by_feature["ranking_eval_phrase_score"]

            # 3. retrieval
            if i & 4:
                cand.skill_features["retrieval_skill_depth"] = 0.90
                cand.evidence.by_feature["retrieval_skill_depth"] = ["Vector search and embeddings experience."]
            else:
                cand.skill_features["retrieval_skill_depth"] = 0.10
                if "retrieval_skill_depth" in cand.evidence.by_feature:
                    del cand.evidence.by_feature["retrieval_skill_depth"]

            # 4. role_fit
            if i & 8:
                cand.career_features["role_family_fit_score"] = 0.95
                cand.evidence.by_feature["role_family_fit_score"] = ["Senior ML Engineer."]
            else:
                cand.career_features["role_family_fit_score"] = 0.20
                if "role_family_fit_score" in cand.evidence.by_feature:
                    del cand.evidence.by_feature["role_family_fit_score"]

            # 5. availability
            if i & 16:
                cand.behavioral_features["availability_multiplier"] = 1.25
                cand.evidence.by_feature["availability_multiplier"] = ["immediate availability"]
            else:
                cand.behavioral_features["availability_multiplier"] = 1.00
                if "availability_multiplier" in cand.evidence.by_feature:
                    del cand.evidence.by_feature["availability_multiplier"]

            # 6. product
            if i & 32:
                cand.career_features["product_company_exposure_months"] = 36.0
                cand.evidence.by_feature["product_company_exposure_months"] = ["Worked at startup building search products."]
            else:
                cand.career_features["product_company_exposure_months"] = 12.0
                if "product_company_exposure_months" in cand.evidence.by_feature:
                    del cand.evidence.by_feature["product_company_exposure_months"]

            # 7. ownership
            if i & 64:
                cand.career_features["ownership_verbs_score"] = 0.85
                cand.evidence.by_feature["ownership_verbs_score"] = ["Shipped ranking models and owned semantic search pipeline."]
            else:
                cand.career_features["ownership_verbs_score"] = 0.30
                if "ownership_verbs_score" in cand.evidence.by_feature:
                    del cand.evidence.by_feature["ownership_verbs_score"]

            candidates.append(cand)

        results = []
        for cand in candidates:
            match = scorer.score(analysis, cand)
            result = generator.generate(analysis, match, cand)
            results.append((cand, match, result))

        # 1. Measure explanation length
        lengths = [len(res.reasoning.split()) for _, _, res in results]
        avg_len = sum(lengths) / len(lengths)

        # 2. Measure duplicates
        explanations = [res.reasoning for _, _, res in results]
        unique_explanations = set(explanations)
        num_duplicates = len(explanations) - len(unique_explanations)

        # 3. Measure empty evidence
        empty_evidence_count = sum(1 for _, _, res in results if not res.evidence)
        # Check that high-fit candidates (fit >= 0.5) always have evidence/strengths
        high_fit_empty_evidence_count = sum(
            1 for cand, _, res in results if cand.semantic_features["jd_semantic_bm25_score"] >= 0.4 and not res.evidence
        )

        # 4. Measure missing concerns (when penalties exist but concerns are empty)
        missing_concerns_count = sum(1 for _, match, res in results if match.penalties and not res.concerns)

        # Print report
        print(f"\n--- Top 100 Stress Test Metrics Report ---")
        print(f"Average explanation length (words): {avg_len:.2f}")
        print(f"Duplicate explanations: {num_duplicates} / 100")
        print(f"Empty evidence recommendations: {empty_evidence_count} / 100")
        print(f"Missing concerns (with penalties active): {missing_concerns_count} / 100")
        print(f"-----------------------------------------\n")

        # Assertions
        # Average length should be reasonable (target: 25 - 75 words across a full population including weak/strong)
        self.assertTrue(25 <= avg_len <= 75, f"Average length {avg_len} is outside expected range (25-75 words)")

        # Duplicate explanations should be low due to templates diversity and combinations of 7 strengths.
        # We assert that the number of duplicates is under 20.
        self.assertLess(num_duplicates, 20, f"Too many duplicate explanations: {num_duplicates}/100")

        # High-fit candidates must always have evidence
        self.assertEqual(
            high_fit_empty_evidence_count,
            0,
            f"Found {high_fit_empty_evidence_count} high-fit candidates with empty evidence",
        )

        # Candidates with penalties must always show concerns
        self.assertEqual(
            missing_concerns_count,
            0,
            f"Found {missing_concerns_count} candidates with active penalties but no concerns",
        )


if __name__ == "__main__":
    unittest.main()

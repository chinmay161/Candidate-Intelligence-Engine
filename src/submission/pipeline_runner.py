"""Orchestrates the entire submission generation workflow."""

import logging
import time
from pathlib import Path
from typing import Iterator

from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.parser import CandidateParser
from jd_parser.jd_parser import JDParser
from ranking.ranker import Ranker
from reasoning.reasoning_generator import ReasoningGenerator
from reasoning.recommendation_builder import RecommendationBuilder
from submission.audit_logger import AuditLogger
from submission.csv_exporter import CSVExporter
from submission.pipeline_config import PipelineConfig
from submission.report_generator import ReportGenerator
from submission.submission_builder import SubmissionBuilder
from submission.submission_models import PipelineResult
from submission.submission_validator import SubmissionValidator

logger = logging.getLogger(__name__)


class PipelineRunner:
    """End-to-end deterministic pipeline execution."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.jd_parser = JDParser()
        self.candidate_parser = CandidateParser()
        self.feature_extractor = CandidateFeatureExtractor()
        self.ranker = Ranker()
        self.reasoning_generator = ReasoningGenerator()
        self.recommendation_builder = RecommendationBuilder()

    def run(self) -> PipelineResult:
        """Execute the pipeline: JD -> Candidates -> Ranking -> Reasoning -> Submission."""
        start_time = time.time()
        try:
            # 1. Parsing JD
            if not self.config.jd_path:
                return PipelineResult(success=False, errors=("jd_path not configured",))
            logger.info("Parsing JD from %s", self.config.jd_path)
            with open(self.config.jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
            jd_analysis = self.jd_parser.parse(jd_text)

            # 2. Streaming Candidates
            if not self.config.candidates_path:
                return PipelineResult(success=False, errors=("candidates_path not configured",))
            logger.info("Streaming candidates from %s", self.config.candidates_path)
            candidate_stream = self.candidate_parser.stream(self.config.candidates_path)

            def streaming_features():
                yield from self.feature_extractor.extract_stream_multiprocess(candidate_stream, chunk_size=1000)

            # 3. Ranking
            logger.info("Ranking candidates...")
            ranking_result = self.ranker.rank(
                analysis=jd_analysis,
                candidates=streaming_features(),
                top_k=self.config.top_k,
                pre_rank_limit=5000,
            )

            # 4. Reasoning
            logger.info("Generating reasoning for top candidates...")
            reasoning_by_candidate = {}
            
            # Re-parse only the top candidates to save memory
            top_ids = {match.candidate_id for match in ranking_result.matches}
            top_records = {}
            # Stream the file one more time
            for candidate in self.candidate_parser.stream(self.config.candidates_path):
                if candidate.candidate_id in top_ids:
                    top_records[candidate.candidate_id] = self.feature_extractor.extract(candidate)
                    if len(top_records) == len(top_ids):
                        break

            for i, match in enumerate(ranking_result.matches):
                record = top_records[match.candidate_id]
                reasoning = self.reasoning_generator.generate(jd_analysis, match, record, rank=i + 1)
                reasoning_by_candidate[match.candidate_id] = reasoning

            # 5. Build Recommendations
            logger.info("Building recommendations...")
            recommendations = self.recommendation_builder.build_many(
                ranking_result.matches, reasoning_by_candidate
            )

            # 6. Submission Builder
            runtime = time.time() - start_time
            submission = SubmissionBuilder.build(
                recommendations=recommendations,
                top_k=self.config.top_k,
                total_candidates_processed=ranking_result.total_candidates,
                pipeline_runtime_seconds=runtime,
            )

            # 7. Validator
            validation = SubmissionValidator.validate(submission, expected_top_k=self.config.top_k)
            if not validation.is_valid:
                errors = "\n".join(validation.errors)
                logger.error("Submission validation failed:\n%s", errors)
                return PipelineResult(success=False, errors=validation.errors)

            # 8. Exporters
            logger.info("Exporting outputs to %s...", self.config.output_dir)
            out_dir = Path(self.config.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            sub_path = out_dir / "submission.csv"
            CSVExporter.export(submission, sub_path)

            report_path = None
            if self.config.enable_reports:
                report_path = out_dir / "evaluation_report.json"
                ReportGenerator.generate(submission, recommendations, report_path)

            audit_path = None
            if self.config.enable_audit_log:
                audit_path = out_dir / "audit_log.json"
                AuditLogger.export(recommendations, audit_path)

            return PipelineResult(
                success=True,
                submission_path=str(sub_path),
                report_path=str(report_path) if report_path else None,
                audit_path=str(audit_path) if audit_path else None,
            )

        except Exception as e:
            logger.exception("Pipeline failed")
            return PipelineResult(success=False, errors=(str(e),))

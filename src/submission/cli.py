"""Command Line Interface for generating submissions."""

import argparse
import logging
import sys

from submission.pipeline_config import PipelineConfig
from submission.pipeline_runner import PipelineRunner


def main():
    parser = argparse.ArgumentParser(description="Generate submission for Candidate Intelligence Engine.")
    parser.add_argument("--jd", required=True, help="Path to JD text file")
    parser.add_argument("--candidates", required=True, help="Path to candidates JSON/JSONL file")
    parser.add_argument("--config", default="configs/default_config.yaml", help="Path to config YAML")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    config = PipelineConfig.from_yaml(args.config)
    # Override paths from CLI
    config = PipelineConfig(
        top_k=config.top_k,
        enable_audit_log=config.enable_audit_log,
        enable_reports=config.enable_reports,
        output_dir=config.output_dir,
        jd_path=args.jd,
        candidates_path=args.candidates,
    )

    runner = PipelineRunner(config)
    result = runner.run()

    if result.success:
        print("Success!")
        print(f"Submission: {result.submission_path}")
        if result.report_path:
            print(f"Report: {result.report_path}")
        if result.audit_path:
            print(f"Audit Log: {result.audit_path}")
    else:
        print("Failed!")
        for error in result.errors:
            print(error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

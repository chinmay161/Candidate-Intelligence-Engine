"""Single-command entrypoint for reproducing the submission CSV.

Usage:
    python rank.py --candidates ./data/candidates.jsonl --out ./submission.csv
"""

import argparse
import sys
from pathlib import Path
import shutil

# Ensure src/ is in the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from submission.pipeline_config import PipelineConfig
from submission.pipeline_runner import PipelineRunner


def main():
    parser = argparse.ArgumentParser(description="Rank candidates for Redrob Hackathon.")
    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates.jsonl file",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to output submission CSV file",
    )
    parser.add_argument(
        "--jd",
        default="data/job_description.txt",
        help="Path to job description text file",
    )
    args = parser.parse_args()

    candidates_path = Path(args.candidates)
    out_path = Path(args.out)
    jd_path = Path(args.jd)

    if not candidates_path.exists():
        print(f"Error: Candidates file not found at {candidates_path}", file=sys.stderr)
        sys.exit(1)

    if not jd_path.exists():
        print(f"Error: Job description file not found at {jd_path}", file=sys.stderr)
        sys.exit(1)

    # Output directory for intermediate files (reports, logs)
    output_dir = out_path.parent if out_path.parent != Path(".") else Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    config = PipelineConfig(
        top_k=100,
        enable_audit_log=True,
        enable_reports=True,
        output_dir=str(output_dir),
        jd_path=str(jd_path),
        candidates_path=str(candidates_path),
    )

    print(f"Starting candidate ranking pipeline...")
    print(f"  JD: {jd_path}")
    print(f"  Candidates: {candidates_path}")
    print(f"  Output Directory: {output_dir}")

    runner = PipelineRunner(config)
    result = runner.run()

    if result.success:
        # Move the output submission.csv to the requested --out destination
        generated_csv = Path(result.submission_path)
        if generated_csv.resolve() != out_path.resolve():
            shutil.copy2(generated_csv, out_path)
            print(f"Copied submission file to: {out_path}")
        else:
            print(f"Generated submission file at: {out_path}")
        
        print("\nPipeline execution completed successfully!")
        print(f"  Submission CSV: {out_path}")
        if result.report_path:
            print(f"  Evaluation Report: {result.report_path}")
        if result.audit_path:
            print(f"  Audit Log: {result.audit_path}")
        sys.exit(0)
    else:
        print("\nPipeline execution failed!", file=sys.stderr)
        for error in result.errors:
            print(f"  Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Candidate Infrastructure Components

## Architecture

These modules provide shared metadata, text, and classification services for later ranking, explainability, and documentation workflows. They are intentionally deterministic and CPU-only.

```text
Candidate
  |
  +--> CandidateTextBuilder
  |       +--> profile / experience / skills / education / full text
  |
  +--> RoleClassifier
  |       +--> RoleClassification(primary_role, confidence, evidence)
  |
  +--> IndustryClassifier
  |       +--> IndustryClassification(primary_industry, confidence, evidence)
  |       +--> product/services/startup/diversity features
  |
  +--> CandidateFeatureExtractor
          |
          +--> FeatureRegistry metadata for emitted feature names
```

## Class Diagram

```text
FeatureDefinition
  name
  group
  priority
  description
  feature_type
  is_penalty
  requires_evidence

FeatureRegistry
  register(definition)
  get(name)
  list_all()
  list_by_group(group)
  list_by_priority(priority)

CandidateTextBuilder
  build_core_text(candidate)
  build_profile_text(candidate)
  build_experience_text(candidate)
  build_skill_text(candidate)
  build_education_text(candidate)
  build_full_text(candidate)

RoleClassifier
  classify(candidate)
  classify_texts(current_title, headline, summary, career_history)

IndustryClassifier
  classify(candidate)
  classify_fields(company_names, industries, descriptions)
  extract_features(candidate)
```

## Data Flow

```text
Raw JSON
  -> CandidateParser
  -> Candidate dataclass
  -> CandidateTextBuilder for canonical retrieval text
  -> RoleClassifier and IndustryClassifier for reusable categorical context
  -> CandidateFeatureExtractor for numeric feature groups
  -> FeatureRegistry for documentation, explainability, and future model tuning
```

## Examples

```python
from pathlib import Path

from candidate_processor import (
    CandidateParser,
    CandidateTextBuilder,
    DEFAULT_FEATURE_REGISTRY,
    IndustryClassifier,
    RoleClassifier,
)

candidate = CandidateParser().parse_json_array(Path("data/sample_candidates.json"))[0]

full_text = CandidateTextBuilder().build_full_text(candidate)
role = RoleClassifier().classify(candidate)
industry = IndustryClassifier().classify(candidate)
critical_features = DEFAULT_FEATURE_REGISTRY.list_by_priority(5)
```

## Notes

- The feature registry catalogs unique feature names. The extractor currently emits `skill_duration_impossibility_count` in both skill and anomaly groups, so the registry stores one canonical definition for that feature name.
- The text builder removes duplicate fragments and normalizes whitespace while preserving readable casing for profile and career text.
- Role classification weights current title and role titles more strongly than profile summary text, which makes non-technical title evidence robust against AI keyword stuffing.
- Industry classification combines employer names, declared industries, and role descriptions. Consulting company names receive strong weight because company identity is often more reliable than generic role text.

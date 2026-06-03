# JD Intelligence Layer

## Scope

The JD intelligence layer converts raw job descriptions into structured, machine-readable analysis. It does not rank candidates, score candidates, or generate recruiter-facing reasoning. Its output is designed to control later ranking behavior dynamically.

## Architecture

```text
Raw JD text + optional title
    |
    v
JDParser
    |
    +-- RoleDetector
    +-- RequirementExtractor
    |       +-- SkillMapper
    +-- NegativeSignalDetector
    +-- WeightGenerator
    |       +-- candidate_processor.FeatureRegistry
    +-- ConfidenceEstimator
    |
    v
JDAnalysis
    |
    v
JDFeatureStore
```

## Package Layout

```text
src/jd_parser/
|-- jd_models.py
|-- dictionaries.py
|-- jd_parser.py
|-- role_detector.py
|-- skill_mapper.py
|-- requirement_extractor.py
|-- negative_signal_detector.py
|-- weight_generator.py
|-- jd_feature_store.py
|-- confidence_estimator.py
`-- __init__.py
```

## Data Flow

`JDParser.parse()` accepts raw JD text plus optional title, company, and location hint. The role detector votes over title, requirement text, responsibility text, and technology stack mentions. The requirement extractor pulls experience bands, canonical skills, industry aliases, location aliases, and behavioral preferences. Negative-signal detection captures explicit exclusion language such as research-only, consulting-only, and non-hands-on concerns.

The weight generator maps these parsed requirements to the existing candidate feature registry and emits grouped weights for semantic, experience, skill, behavioral, career, education, logistics, and anomaly features.

## Output Shape

```json
{
  "role_family": "AI_ENGINEER",
  "required_skills": [],
  "preferred_skills": [],
  "optional_skills": [],
  "negative_signals": [],
  "experience_min": 5,
  "experience_max": 9,
  "industries": ["hrtech", "marketplace"],
  "locations": ["pune", "noida", "hybrid"],
  "behavioral_preferences": ["ownership", "product_thinking"],
  "feature_weights": {
    "semantic": {},
    "experience": {},
    "skill": {},
    "behavioral": {},
    "career": {},
    "education": {},
    "logistics": {},
    "anomaly": {}
  },
  "confidence": 0.0
}
```

## Weight Logic

Weights are generated from parsed JD content:

- Role family boosts the candidate features that matter for that role.
- Required skills receive stronger weight than preferred skills; optional skills remain weak tie-breakers.
- Industry aliases boost product, marketplace, HR-tech, and domain-fit features.
- Location aliases boost location, relocation, India, and work-mode features.
- Behavioral preferences boost ownership, startup exposure, product impact, experimentation, and hands-on features.
- Negative signals boost the corresponding penalty or anomaly features.

The generator emits every candidate feature group so later rankers can consume a stable shape even when a JD is sparse.

## Example

```python
from jd_parser import JDParser

analysis = JDParser().parse(
    '''
    Senior AI Engineer for an HR Tech marketplace.
    Required: 5-9 years, Python, semantic search, embeddings, Pinecone,
    Elasticsearch, learning to rank, NDCG, and production systems.
    Must be hands-on with ownership and product thinking.
    Pune or Noida, hybrid.
    ''',
    title='Senior AI Engineer',
)

analysis.role_family
analysis.required_skills
analysis.feature_weights.by_group['skill']['retrieval_skill_depth']
```

## Future Integration

The later ranking layer should consume `JDAnalysis.feature_weights` alongside candidate feature records. The reasoning generator should use `JDAnalysis` to frame why particular candidate evidence is relevant to a specific role, while still grounding statements in candidate evidence rather than JD assumptions.

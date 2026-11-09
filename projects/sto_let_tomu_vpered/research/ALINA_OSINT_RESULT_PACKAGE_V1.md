# ALINA OSINT RESULT PACKAGE v1

## Purpose

This file defines the contract between an external OSINT system and ALINA.

ALINA sends an object-identification request.
The OSINT system returns one normalized package.

ALINA must not depend on how the OSINT system searched.
It consumes only this package.

## Core rule

OSINT_RESULT != ANALYTICAL_CANON

The package contains discovered evidence, candidate facts, source provenance, versions and confidence.
ALINA performs its own downstream comparison, evidence validation and canon admission.

## Top-level structure

```json
{
  "schema_version": "1.0",
  "package_id": "OSINT-...",
  "mode": "SIMULATED_OSINT | OFFICIAL_DIRECT | LIVE_OSINT",
  "simulation": false,
  "request": {},
  "object": {},
  "identity": {},
  "authority": {},
  "bibliography": {},
  "versions": [],
  "texts": [],
  "completeness": {},
  "comparison": {},
  "relations": [],
  "sources": [],
  "evidence": [],
  "questions": [],
  "findings": [],
  "risks": [],
  "unresolved": [],
  "recommendations": [],
  "quality": {},
  "generated_at": ""
}
```

# 1. request

What ALINA asked the OSINT system to investigate.

Fields:
- request_id
- project_id
- object_id
- object_type
- title_hint
- author_hint
- date_hint
- file_fingerprint
- questions
- requested_outputs
- priority

# 2. object

Normalized target object.

Fields:
- object_id
- object_type
- canonical_title
- alternate_titles
- author
- issuing_authority
- document_number
- identifiers
- date
- publication_date
- adoption_date
- effective_from
- effective_to
- form
- language
- cycle_or_collection
- sequence_number
- description

# 3. identity

OSINT conclusion about what the object is.

Fields:
- status
  - IDENTIFIED
  - PROBABLE
  - AMBIGUOUS
  - NOT_IDENTIFIED
- confidence
- match_basis
- competing_candidates
- identity_evidence_ids

# 4. authority

Where the authoritative/official reference comes from.

Fields:
- authority_status
  - OFFICIAL_PRIMARY
  - OFFICIAL_PUBLICATION
  - OFFICIAL_REGISTER
  - AUTHORIZED_COPY
  - BIBLIOGRAPHIC_REFERENCE
  - TRUSTED_SECONDARY
  - UNVERIFIED_COPY
  - NOT_FOUND
- preferred_source_id
- issuing_body
- official_record_id
- official_url
- verification_date
- verification_notes

Important:
OFFICIAL_PRIMARY means the publication/source is authoritative.
It does not mean ALINA may skip text/version comparison.

# 5. bibliography

Descriptive metadata.

Possible fields:
- first_publication_year
- first_publication_date
- publisher
- place
- isbn
- issn
- series
- volume
- edition
- pages
- catalog_records
- library_records

# 6. versions

Known versions/editions/revisions.

Each record:
- version_id
- title
- edition
- revision
- date
- publisher_or_authority
- identifiers
- status
- source_ids
- text_available
- normalized_text_hash
- relationship_to_other_versions

Relationships:
- ORIGINAL
- REVISED_FROM
- SUPERSEDES
- AMENDS
- REPRINT_OF
- DERIVED_FROM
- TEXTUALLY_IDENTICAL_TO

# 7. texts

Texts that OSINT located.

Each text record:
- text_id
- version_id
- source_id
- access_type
  - FULL_TEXT
  - PREVIEW
  - METADATA_ONLY
- format
- language
- checksum
- normalized_text_hash
- size_bytes
- completeness_status
- retrieval_status
- local_cache_ref
- retrieval_time

Never embed copyrighted full text into the OSINT package stored in GitHub.
Use references/checksums/local cache paths.

# 8. completeness

OSINT assessment of whether the local/project text is complete.

Fields:
- status
  - COMPLETE
  - LIKELY_COMPLETE
  - PARTIAL
  - FRAGMENT
  - UNKNOWN
- confidence
- expected_structure
- observed_structure
- missing_sections
- extra_sections
- basis

# 9. comparison

Recommended text/version comparison plan.

Fields:
- local_text_id
- reference_text_id
- reference_version_id
- comparison_status
- comparison_priority
- comparison_reason
- expected_diff_type
- requires_text_download

Possible statuses:
- READY_TO_COMPARE
- REFERENCE_PENDING
- NO_COMPARISON_NEEDED
- MULTIPLE_CANDIDATES
- BLOCKED

# 10. relations

Relationships to other corpus objects.

Examples:
- PART_OF_CYCLE
- PART_OF_COLLECTION
- AMENDS
- REFERENCES
- SUPERSEDES
- SEQUEL_TO
- PREQUEL_TO
- VERSION_OF
- REPRINT_OF

Each relation:
- source_object_id
- relation_type
- target_object_id
- confidence
- evidence_ids

# 11. sources

Every discovered external source.

Each record:
- source_id
- source_type
- title
- organization
- url
- authority_rank
- access_date
- status
- content_type
- supports
- notes

Authority rank:
- 100 OFFICIAL_PRIMARY
- 95 OFFICIAL_PUBLICATION
- 90 OFFICIAL_REGISTER
- 80 AUTHORIZED_COPY
- 70 BIBLIOGRAPHIC_REFERENCE
- 60 TRUSTED_SECONDARY
- 30 COMMUNITY
- 10 UNVERIFIED

# 12. evidence

Evidence supporting OSINT findings.

Each record:
- evidence_id
- source_id
- field
- value
- excerpt_or_fact
- location
- confidence
- verification_status

Do not copy large source passages.
Store only minimal evidence necessary for verification.

# 13. questions

Answer set to ALINA questions.

Each record:
- question_id
- question
- answer
- confidence
- status
- evidence_ids

Statuses:
- ANSWERED
- PARTIAL
- CONFLICT
- NOT_FOUND
- NOT_APPLICABLE

# 14. findings

Important discovered facts.

Each record:
- finding_id
- type
- statement
- confidence
- evidence_ids
- impact

Finding types may include:
- IDENTITY
- VERSION
- DATE
- AUTHORSHIP
- AUTHORITY
- COMPLETENESS
- TEXT_VARIANT
- MISSING_OBJECT
- DUPLICATE
- CONFLICT
- RELATION

# 15. risks

Things that may make downstream analysis unreliable.

Examples:
- UNCERTAIN_IDENTITY
- UNKNOWN_VERSION
- PARTIAL_TEXT
- MULTIPLE_EDITIONS
- NO_OFFICIAL_SOURCE
- SOURCE_CONFLICT
- COPYRIGHT_RESTRICTION
- OCR_QUALITY_LOW

Each risk:
- risk_id
- type
- severity
- description
- affected_fields
- mitigation

# 16. unresolved

Questions that OSINT could not resolve.

Each item:
- unresolved_id
- question
- reason
- required_action
- blocking
- priority

# 17. recommendations

What ALINA should do next.

Examples:
- USE_REFERENCE_VERSION
- DOWNLOAD_OFFICIAL_TEXT
- RUN_TEXT_COMPARISON
- REQUEST_HUMAN_REVIEW
- ACCEPT_BIBLIOGRAPHIC_IDENTITY
- KEEP_MULTIPLE_VERSIONS
- DO_NOT_START_CANON_ANALYSIS

# 18. quality

Package-level quality.

Fields:
- identity_confidence
- authority_confidence
- completeness_confidence
- version_confidence
- source_coverage
- evidence_coverage
- unresolved_count
- blocking_count
- package_status

Package statuses:
- READY
- READY_WITH_WARNINGS
- REVIEW
- BLOCKED

## Minimal package accepted by ALINA

ALINA may accept a package only when it has:
- package_id
- object_id
- identity.status
- identity.confidence
- sources
- questions
- unresolved
- quality.package_status

## Gate to Corpus Lab

READY:
- identity established
- at least one trusted/authoritative reference
- comparison target known OR comparison not required

READY_WITH_WARNINGS:
- identity established
- reference exists
- non-blocking version/completeness uncertainty remains

REVIEW:
- identity or version has competing candidates

BLOCKED:
- cannot determine what object/text is being analyzed

## Important simulation rule

SIMULATED_OSINT can populate all fields needed to test ALINA workflows.

But simulated results must include:
```
"simulation": true
```

and must never claim:
- VERIFIED_EXTERNAL
- OFFICIAL_PRIMARY
- OFFICIAL_REGISTER

unless these values came from a real source retrieval.

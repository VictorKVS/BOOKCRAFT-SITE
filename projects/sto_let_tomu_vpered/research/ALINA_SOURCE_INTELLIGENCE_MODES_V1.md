# ALINA SOURCE INTELLIGENCE MODES v1

## Goal
Separate corpus engineering from real external OSINT during development.

ALINA can operate in three Source Intelligence modes.

### 1. SIMULATED_OSINT
Default development mode.

ALINA behaves as if an external OSINT service received research questions and returned a complete structured answer package.

Rules:
- no claim that internet research actually occurred;
- every result is marked SIMULATED_OSINT;
- no invented official URL may be represented as verified;
- known local catalog metadata may be reused;
- synthetic authority/source records must be marked SIMULATED;
- used to exercise downstream Corpus Lab, Text Comparison, dashboards and quality gates.

### 2. OFFICIAL_DIRECT
Use when a known official/authoritative source endpoint is configured.

Workflow:
object -> known authority source -> retrieve -> checksum -> metadata -> version/completeness -> compare.

This mode may bypass broad OSINT discovery, but it does NOT bypass:
- provenance capture;
- checksum;
- edition/revision identification;
- effective/current status checks for regulatory documents;
- text comparison when multiple versions exist.

### 3. LIVE_OSINT
Use only when discovery is required.

Workflow:
questions -> external search/connectors -> candidate sources -> authority ranking -> retrieval -> verification -> comparison -> result package.

## OSINT question packet

For every corpus object ALINA sends a standard question set:

Q1. What is this object?
Q2. What is its canonical title?
Q3. Who is the author / issuing authority?
Q4. What is the publication/adoption date?
Q5. What stable identifiers exist?
Q6. What aliases or alternate titles exist?
Q7. Is it part of a cycle / collection / legal hierarchy?
Q8. What editions/revisions are known?
Q9. Which source is authoritative?
Q10. Is an authoritative full text available?
Q11. Is the local text complete?
Q12. Which known version best matches the local text?
Q13. Are there other text variants?
Q14. What should be used as the comparison reference?
Q15. What unresolved provenance/version questions remain?

## Result package

source_intelligence/<object_id>/osint_result.json

Fields:
- mode
- simulation
- object_id
- object_type
- identification
- canonical_metadata
- authority_sources
- versions
- completeness
- comparison_targets
- unresolved
- confidence
- generated_at

## Production rule

SIMULATED_OSINT may unlock UI and pipeline development but must never set:
authority_status = OFFICIAL_PRIMARY
or
verification_status = VERIFIED_EXTERNAL

unless the result came from OFFICIAL_DIRECT or LIVE_OSINT with real provenance.

## Official-direct rule

A known official source can be used directly as the authoritative retrieval source. Broad OSINT discovery may be skipped.

However:
"official source" means provenance/authenticity of that publication is trusted;
it does not mean all downstream interpretation, current applicability, completeness of a legal chain, or cross-version consistency is automatically solved.

# ALINA UNIVERSAL CORPUS OBJECT CONTRACT v1

## Purpose
A corpus object is the unit shown in Corpus Lab / Knowledge Base lists. It may represent a literary work, legal act, technical standard, scientific paper, internal document, or another versioned source object.

## Common fields

```json
{
  "object_id": "stable-id",
  "object_type": "LITERARY_WORK | LEGAL_ACT | STANDARD | SCIENTIFIC_PAPER | INTERNAL_DOCUMENT",
  "title": "",
  "date": null,
  "author": null,
  "issuing_authority": null,
  "document_number": null,
  "form": null,
  "aliases": [],
  "version": null,
  "edition": null,
  "effective_from": null,
  "effective_to": null,
  "source_id": null,
  "source_file": null,
  "authority_sources": [],
  "authority_status": "AUTHORITY_SOURCE_PENDING",
  "completeness_status": "UNKNOWN",
  "version_status": "VERSION_NOT_VERIFIED",
  "confidence": 0.0,
  "provenance": {},
  "notes": []
}
```

## UI rule
Clicking an object in the corpus list opens its object card.

The card must show all known attributes and must explicitly display UNKNOWN / NOT VERIFIED for fields that have not yet been established. The UI must never infer official status from a filename or a secondary catalog.

## Literary profile
Additional fields may include:
- cycle
- publication_year
- literary form
- semantic/catalog order
- internal chronology candidate
- chronology confidence
- matched heading

## Regulatory profile
Additional fields may include:
- issuing authority
- document number
- adoption date
- publication date
- effective date
- repeal date
- current revision
- amendments
- official publication/register URLs
- legal status
- scope
- referenced documents

## Version-comparison status
- IDENTICAL_FILE
- IDENTICAL_NORMALIZED_TEXT
- MINOR_TEXT_VARIANT
- SIGNIFICANT_TEXT_VARIANT
- EDITION_VARIANT
- VERSION_NOT_VERIFIED

## Completeness status
- FOUND_IN_CORPUS
- POSSIBLE_MATCH_REVIEW
- MISSING_FROM_CORPUS
- PARTIAL_TEXT
- COMPLETE_TEXT
- COMPLETENESS_NOT_VERIFIED

## Authority status
- OFFICIAL_PRIMARY
- OFFICIAL_PUBLICATION
- OFFICIAL_REGISTER
- AUTHORIZED_COPY
- BIBLIOGRAPHIC_REFERENCE
- TRUSTED_SECONDARY
- UNVERIFIED_COPY
- AUTHORITY_SOURCE_PENDING

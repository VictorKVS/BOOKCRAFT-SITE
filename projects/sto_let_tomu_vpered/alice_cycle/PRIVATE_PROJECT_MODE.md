# PRIVATE PROJECT MODE

## Default

Training projects are PRIVATE BY DEFAULT.

### Local-only data
The following must not be committed to GitHub or published by the application:
- uploaded book files
- user manuscripts
- author plans
- project notes
- generated continuation drafts
- private knowledge bases
- private world models
- relationship/intimacy state
- unpublished plot branches

### Repository-safe data
Only platform code, schemas, generic test fixtures and explicitly approved derived non-private artifacts may enter Git.

## Network policy

Default:
- external research OFF
- telemetry OFF for private content
- cloud model calls OFF unless explicitly enabled
- no background upload
- no public project URL

## UI contract

Every private project must visibly show:
PRIVATE LOCAL MODE / LOCAL ONLY

Any action that sends project content outside the local runtime must require an explicit mode change or authorization.

## Development phase

For the current browser-only prototype, selected files remain File objects in browser memory and are not uploaded by the UI.

The future local backend must preserve the same policy and store project data outside the public repository.

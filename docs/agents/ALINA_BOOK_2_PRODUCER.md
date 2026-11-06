# ALINA BOOK 2 — Producer / Showrunner Agent

## Mission

**ALINA BOOK 2 Producer** is the top-level orchestration agent for fiction production.

It does not replace ALINA Analyst or ALINA Writer.

- **ALINA Analyst** builds and maintains the truth/state model of the story world.
- **ALINA Writer** creates prose, scenes and alternative branches.
- **ALINA BOOK 2 Producer** decides what must be created next, why, in what order, with which constraints, and whether the result is good enough to move forward.

In short:

```text
ANALYST = UNDERSTANDS
WRITER  = WRITES
PRODUCER = DIRECTS THE WHOLE PROJECT
```

---

## Producer responsibility

The Producer owns:

- project concept;
- target audience;
- genre mix;
- format;
- book/series structure;
- commercial and creative positioning;
- story bible;
- long arcs;
- book arcs;
- episode/chapter objectives;
- pacing;
- reveal scheduling;
- escalation;
- character arc coordination;
- continuity governance;
- quality gates;
- rewrite decisions;
- release readiness;
- versioning.

The Producer must never silently rewrite canon. Canon changes are explicit decisions.

---

## Core pipeline

```text
IDEA / SOURCE STORY / USER BRIEF
        ↓
ALINA BOOK 2 PRODUCER
        ↓
PROJECT BRIEF
        ↓
ALINA ANALYST
        ↓
NARRATIVE MODEL / CANON / OPEN THREADS
        ↓
PRODUCER PLANNING
        ↓
STORY / SERIES ARCHITECTURE
        ↓
ALINA WRITER
        ↓
DRAFT
        ↓
CRITIC LAYER
        ↓
PRODUCER DECISION
   ┌────┼─────┐
   ↓    ↓     ↓
ACCEPT REPAIR REPLAN
        ↓
NEXT ITERATION
        ↓
BOOK / EPISODE / SERIES RELEASE
```

---

# 1. Producer modes

## 1.1 CREATE

Build a new project from:
- idea;
- premise;
- character;
- world;
- short story;
- user brief.

Output:
- project brief;
- genre vector;
- audience;
- tone;
- concept;
- logline;
- core conflict;
- target format;
- initial arc.

## 1.2 ADAPT

Take an existing story and transform it into:
- longer novel;
- series;
- episode structure;
- alternate version;
- genre-shifted version;
- retelling.

The original source remains preserved as reference canon unless user explicitly authorizes replacement.

## 1.3 CONTINUE

Continue an existing work while preserving:
- canon;
- style;
- character logic;
- unresolved threads;
- world rules;
- chronology.

## 1.4 SERIES

Turn one story/world into a multi-book or multi-season universe.

The Producer creates:
- series bible;
- long arc;
- installment arcs;
- escalation model;
- reveal schedule;
- character arc matrix;
- continuity matrix;
- future hooks.

## 1.5 REWRITE

Rework a weak or rejected section.

Reasons may include:
- broken pacing;
- contradiction;
- weak motivation;
- flat dialogue;
- missing payoff;
- unresolved setup;
- style drift;
- canon violation.

## 1.6 BRANCH

Create an explicit alternate timeline from a selected divergence point.

---

# 2. Producer project brief

Every project starts with a machine-readable production brief.

Example:

```yaml
project_id: alina-book-2-demo
title:
format: novel | series | episode | short_story
target_length:
audience:
age_rating:
genres:
  science_fiction: 0.8
  thriller: 0.6
tone:
pov:
central_premise:
core_conflict:
themes:
must_keep:
must_avoid:
creative_freedom:
commercial_target:
release_model:
```

---

# 3. Producer hierarchy

```text
PROJECT
├── SERIES ARC
│   ├── BOOK 1 ARC
│   │   ├── ACT
│   │   │   ├── CHAPTER
│   │   │   │   └── SCENE
│   ├── BOOK 2 ARC
│   └── BOOK N ARC
│
├── CHARACTER ARCS
├── WORLD ARCS
├── CONFLICT ARCS
├── REVEAL SCHEDULE
└── CONTINUITY STATE
```

The Producer tracks all levels simultaneously.

---

# 4. Producer works with state, not only text

The Producer consumes structured state:

```text
CANON
CHARACTERS
RELATIONS
BELIEFS
SECRETS
LOCATIONS
TIMELINE
WORLD RULES
PLOT THREADS
PROMISES
PAYOFFS
UNRESOLVED QUESTIONS
CHARACTER ARCS
STYLE PROFILE
AUDIENCE PROFILE
```

The output of each approved scene updates the production state.

---

# 5. Story economy

The Producer should treat every chapter or scene as an investment.

A scene must do at least one meaningful job:

- advance plot;
- change character state;
- reveal information;
- create a question;
- resolve a question;
- increase conflict;
- deepen relationship;
- alter the world state;
- prepare a payoff.

A scene that does none of these is a candidate for removal or merge.

---

# 6. Setup → Development → Payoff tracking

The Producer maintains a promise ledger.

Example:

```text
SETUP S-014
  ↓
DEVELOP S-031 / S-046
  ↓
PAYOFF S-071
```

For every major setup, track:
- introduced_at;
- reinforced_at;
- payoff_target;
- payoff_status;
- importance;
- expected audience memory.

This helps avoid forgotten plot threads.

---

# 7. Reveal scheduler

Secrets and discoveries are planned, not random.

For each reveal:

```text
FACT
WHO KNOWS
WHO SUSPECTS
WHO IS WRONG
WHEN READER LEARNS
WHEN CHARACTER LEARNS
WHAT CHANGES AFTER REVEAL
```

This is critical for detective, thriller, mystery and long series.

---

# 8. Character arc matrix

Example:

```text
CHARACTER
  initial_state
  desire
  fear
  lie_believed
  external_goal
  internal_need
  turning_points
  losses
  gains
  final_state
```

The Producer checks that story events actually move the arc.

---

# 9. Genre-aware production

The Producer must use genre-specific planning profiles.

Examples:

## Detective
- crime;
- suspects;
- clues;
- false clues;
- alibis;
- motive;
- reveal order;
- fairness to reader.

## Science fiction
- world rules;
- technology constraints;
- plausibility;
- second-order consequences;
- consistency.

## Drama
- relationships;
- emotional escalation;
- moral conflict;
- irreversible decisions.

## Thriller
- threat escalation;
- deadlines;
- pressure;
- pursuit;
- reversals.

## Series fiction
- local arc;
- global arc;
- recurring hooks;
- escalation without repetition.

---

# 10. Producer quality gates

A draft cannot move forward only because prose is fluent.

Minimum gates:

```text
CANON CONSISTENCY
CONTINUITY
CHARACTER LOGIC
SCENE PURPOSE
PACING
SETUP/PAYOFF
GENRE CONTRACT
STYLE CONSISTENCY
REPETITION CONTROL
USER CONSTRAINTS
```

Each gate returns:

```text
PASS
CONDITIONAL
REPAIR
REPLAN
REJECT
```

---

# 11. Producer decision loop

```text
PLAN
 ↓
WRITE
 ↓
CHECK
 ↓
DECIDE

IF PASS:
  accept and update state

IF REPAIR:
  send explicit defects to Repair Agent

IF REPLAN:
  modify scene/chapter/arc plan

IF REJECT:
  discard draft but preserve evidence
```

---

# 12. Multi-writer mode

Producer may request several candidate drafts.

```text
SCENE CONTRACT
   ↓
WRITER A
WRITER B
WRITER C
   ↓
CRITIC
   ↓
PRODUCER
   ↓
BEST / SYNTHESIS / REWRITE
```

The Producer does not assume the largest model is automatically the best writer.

---

# 13. Brain model policy

Producer is not permanently tied to one LLM.

```text
PRODUCER AGENT
  └── BRAIN SLOT
        ├── CHAMPION
        ├── CHALLENGER
        └── FALLBACK
```

Brain replacement requires role-specific qualification.

Producer evaluation should test:
- long-horizon planning;
- consistency;
- prioritization;
- dependency tracking;
- rewrite decisions;
- series coherence;
- constraint handling.

---

# 14. Separation of authority

Authority order:

```text
USER INTENT
    ↓
LOCKED CANON
    ↓
ANALYST VERIFIED STATE
    ↓
PRODUCER PLAN
    ↓
WRITER DRAFT
    ↓
STYLE PREFERENCE
```

The Writer cannot override canon.

The Producer cannot silently change a user-locked constraint.

The Analyst does not decide artistic direction.

---

# 15. ALINA BOOK 2 system

```text
                   USER / CREATOR
                         ↓
                ALINA BOOK 2 PRODUCER
                         ↓
            ┌────────────┼────────────┐
            ↓            ↓            ↓
      ALINA ANALYST   ALINA WRITER   RESEARCH
            ↓            ↓            ↓
       CANON/STATE      DRAFTS      MATERIAL
            └────────────┼────────────┘
                         ↓
                     CRITICS
                         ↓
                 PRODUCER DECISION
                         ↓
                 VERSIONED STORY
                         ↓
                 BOOK / SERIES
```

---

# 16. Future extension

ALINA BOOK 2 Producer can later coordinate:

- illustrator / visual agent;
- cover designer;
- world-map generator;
- audiobook adaptation;
- screenplay adaptation;
- comic scene generator;
- marketing copy agent;
- publishing pipeline.

The Producer remains the single project-level orchestration authority.

---

## Core principle

> **ALINA BOOK 2 is not one model writing a book. It is a controlled production system where analysis, planning, writing, criticism, continuity and release are separate responsibilities.**

# MVP-14A2 — Work Boundary Resolver

The source DOCX contains at least two separate works.

Detected structure:
- primary work starts at paragraph 0: "Сто лет тому вперед (Гостья из будущего)";
- parts of the primary work are marked as Heading2 with "Часть 1" and "Часть 2";
- a new Heading2 at paragraph 3977 is "Пленники астероида";
- therefore the primary work ends at paragraph 3976.

This stage creates:
- `structure/work_boundaries.json`
- `structure/primary_work_chunk_index.json`
- local source chunks under `sources/work_chunks/sto_let_tomu_vpered/`
- `runs/mvp14a2_work_boundary.json`

Only primary-work chunks are eligible for the next semantic canon pass.

The original full-source chunk set remains untouched for audit/reproducibility.

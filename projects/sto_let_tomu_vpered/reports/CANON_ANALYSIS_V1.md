# CANON ANALYSIS V1 — «Сто лет тому вперёд»

## Status

`CANON_ACCEPTANCE: CONDITIONAL`

Причина: базовый персонажный и визуальный канон Алисы зафиксирован, но полный роман ещё не прогнан через автоматический поэпизодный индекс всех персонажей, объектов, событий и временных состояний.

## 1. Source-derived literary canon

### Алиса Селезнёва

Source analysis supports:

- возраст — примерно двенадцать лет;
- светлые коротко подстриженные волосы;
- голубые глаза;
- длинноногая, естественная внешность;
- в Космозо появляется в красном комбинезоне;
- имеет устойчивую связь с Бронтей и уверенно взаимодействует с крупным животным;
- знакома с космобиологией и опытом космических путешествий;
- знает назначение миелофона и использует его для исследования животных;
- умеет пользоваться машиной времени в контексте сюжета;
- наблюдательна: при опасности проверяет людей и окружение;
- способна быстро заметить отсутствие нужного человека и перейти к действию;
- признаёт собственные ошибки и ответственность за потерю миелофона;
- действует смело, но не является безошибочной.

## 2. User-locked Russian cultural visual canon

For this adaptation the user requires a Russian-audience recognizable Alice.

This is stored separately from literary canon:

```text
LITERARY CHARACTER
+
USER_LOCKED_RUSSIAN_VISUAL_CANON
=
ALINA COMIC / ILLUSTRATION ALICE
```

The cultural visual lock is inspired by the recognizable Soviet screen tradition of «Гостья из будущего», while the generated character must remain an original adaptation design rather than a literal replica of a real performer.

Locked adaptation traits:

- 12–13-year-old appearance;
- slim, tall-for-age proportions;
- light brown / fair hair;
- youthful natural face;
- calm, intelligent, slightly serious expression;
- no glamour;
- no adult makeup;
- no adult body proportions;
- stable face/hair/proportions across panels.

## 3. Character behaviour lock

A new story featuring Alice should normally follow:

```text
OBSERVE ANOMALY
→ FORM HYPOTHESIS
→ VERIFY
→ ACT
→ NOTICE CONTRADICTION
→ CORRECT HYPOTHESIS
→ ACCEPT RESPONSIBILITY
```

This is preferred over:

```text
INSTANT OMNISCIENCE
→ ACTION-HERO RESPONSE
→ GLOBAL THREAT EXPOSITION
```

## 4. Story-generation constraints

A continuation/adaptation may introduce new:
- scientific mysteries;
- animals;
- locations;
- technologies;
- children / researchers;
- adventures.

But every new element starts as `HYPOTHESIS/NEW_STORY_CANON` and is committed only after verification.

The story must preserve:
- Alice's age;
- intellectual/ethical profile;
- existing known relationships;
- established world logic;
- knowledge boundaries;
- Russian cultural visual identity lock.

## 5. Comic adaptation constraints

Each panel containing Alice must inherit:

- `character_id=alisa_selezneva`;
- `visual_identity_lock=ALISA_RU`;
- current outfit;
- current carried objects;
- scene knowledge state;
- pose/gaze/expression;
- previous accepted visual reference.

The Visual Critic must reject:
- face drift;
- age drift;
- adultization;
- hair identity drift beyond an explicitly approved scene change;
- wrong person count;
- incorrect outfit continuity;
- scene action contradicting narrative state.

## 6. Next automated analysis stage

```text
FULL BOOK
→ chapter/scene segmentation
→ character registry
→ location/object registry
→ event graph
→ timeline
→ knowledge/belief graph
→ world-rule registry
→ per-character bible
→ visual bible
→ comic adaptation candidates
```

This V1 report establishes the acceptance rules that the full analysis must obey.

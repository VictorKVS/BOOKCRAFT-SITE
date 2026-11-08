# ALICE FB2 SOURCE AUDIT

Source: **Весь Кир Булычев в одном томе (СИ)**  
Author metadata: **Кир Булычев**  
Size: **64,807,921 bytes**

## Result

The FB2 contains a top-level section:

`ПРИКЛЮЧЕНИЯ АЛИСЫ (цикл)`

The current 52-work ALICE manifest can be matched against this source at **51 / 52** works.

### Missing from this source

- ALICE-029 — **Звёздный пёс**

### Composite containers found

- НЕПОСЕДА
  - Заповедник сказок
  - Козлик Иван Иванович
  - Лиловый шар
- ГАЙ-ДО
  - Гай-до
  - Узники «Ямагири-Мару»
  - Конец Атлантиды
  - Город без памяти
- АЛИСА И ЕЕ ДРУЗЬЯ В ЛАБИРИНТАХ ИСТОРИИ
  - Древние тайны
  - Пашка-троглодит
  - Чулан Синей Бороды
  - Драконозавр
  - Принцы в башне
- ПОВЕСТИ ДЛЯ ДЕТЕЙ МЛАДШЕГО ВОЗРАСТА
  - Королева пиратов на острове сказок
  - Колдун и Снегурочка
  - Алиса на планете загадок
  - Алиса и дракон
  - Алиса и притворщики

## Metadata conflicts detected

1. Source heading: **ПЛАНЕТА ДЛЯ ТИТАНОВ**  
   Bibliographic manifest: **Планета для тиранов**  
   Treat as a source metadata conflict. Preserve both values and resolve through external bibliographic evidence.

2. Source heading: **Королева пиратов на острове сказок**  
   Manifest: **Королева пиратов на планете сказок**  
   Treat as title variant/conflict until bibliographic normalization.

## Ingest rule

Do not commit the full copyrighted source text into the repository.

Keep:
- source checksum
- source metadata
- work boundaries
- structural indexes
- evidence references
- derived claims / graph data

Next step:
`FB2 -> Alice top-level section -> per-work source units -> ALICE-001..052 mapping -> chapter indexes`.

# Writing for the owner: ASD-STE100

Everything sly writes for people follows ASD-STE100 Simplified Technical English (STE). This
applies to messages, questions and reports to the owner, and to the docs sly writes and
maintains (`docs/INTENT.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/CLEANUP.md`).
It does not apply to code, code comments, or messages between agents.

This page is a summary of the main rules. The official specification and dictionary come from
ASD (asd-ste100.org).

## Words

- Use simple, common words, with one meaning for each word. Use the word in that meaning only.
- Use the same word for the same thing every time. Do not change words for variety.
- Project names are technical names: the names of pieces, folders, commands and files. Use
  them exactly as they are, and explain each one the first time.
- Do not use phrasal verbs ("set up", "carry out", "find out"). Use one verb ("install", "do",
  "find").
- Common replacements:

| Do not write | Write |
|---|---|
| utilize, leverage | use |
| ensure, verify | make sure |
| commence, initiate | start |
| terminate, cease | stop |
| approximately | about |
| prior to | before |
| subsequent to | after |
| in order to | to |
| sufficient | enough |
| modify | change |
| assist, facilitate | help |
| require | need |
| indicate | show |
| additional | more |

## Sentences

- **Instructions:** 20 words or fewer. **Descriptions:** 25 words or fewer.
- One instruction in each sentence. Put each step of a procedure in its own numbered line.
- Write the condition first: "If the import fails, do step 3."
- Use the active voice: "The check found two problems", not "Two problems were found".
- Use the imperative for instructions: "Run the check", not "You should run the check".
- Use these verb tenses only: simple present, simple past, simple future ("finds", "found",
  "will find").
- Do not use the "-ing" form of a verb, except in technical names.
- Do not leave out words to make a sentence shorter. Keep "the", "a", "is" and "that".
- Do not join more than three nouns together ("the import duplicate check" is the limit).

## Paragraphs

- One topic in each paragraph. Six sentences or fewer.
- Start with the most important information.

## Warnings and cautions

- Use a warning for a risk to data or work that cannot be undone. Use a caution for a risk of a
  smaller problem.
- Start with a short, clear command: "Make a backup of the data file before you do this step."

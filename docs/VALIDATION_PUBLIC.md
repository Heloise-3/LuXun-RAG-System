# Validation notes — November 2026

## Automated checks

The offline suite has 24 passing cases covering:

- zero vectors, incompatible vector dimensions and selective hybrid ranking;
- avoiding repeated query analysis;
- same-origin page/assets and API input validation;
- sanitized provider errors and timeouts;
- duplicate passages, provenance fields and stale-index detection;
- query tags constrained to the existing corpus vocabulary.

Provider interactions in these automated tests are mocked. They do not measure generation quality.

## Real provider checks

The 11 newly reviewed excerpts were successfully embedded. After the original three passages were restored, those three were also embedded successfully. The active corpus and index contain 14 matching entries, each with a 4,096-dimensional embedding.

Two authorized full browser requests used real DeepSeek and SiliconFlow APIs. The first completed in approximately 7.52 seconds and exposed out-of-vocabulary query tags. The analyzer prompt and validation were then constrained to dictionary.md, with regression tests added.

A second full browser request after restoring the original three passages completed in approximately 6.39 seconds. The returned tags were all in the existing vocabulary, and the retrieval results were original passage IDs 1 and 3. The page displayed generated text, both actual reference passages, scores and context.

The two runs are not a controlled before/after evaluation: corpus membership, query-vocabulary constraints and stochastic model output all affect the result. No general relevance gain or literary-quality improvement is claimed.

## Interface revision

The interface was simplified to input, result and source-reference areas. The branding header, footer signature and promotional slogans were removed. The provenance and generated-text distinctions remain.

Visual checks for this revision replayed the saved response from the second real run. They did not make additional paid model calls. The current screenshots demonstrate layout and rendering of a previously recorded result; they are not new generation evidence.

## Limits

No public deployment, systematic style evaluation or educational-outcome study has been performed. These observations are functional checks on a small prototype.

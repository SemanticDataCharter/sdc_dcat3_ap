# sdc_dcat3_ap PRD: one SDC model, described in DCAT-AP 3.0.1

**Status:** v0.1, 9 October 2026, DRAFT for Tim. The third projection demo of the projections track (ContentStrategy
lane 5.6): a public repository in the SemanticDataCharter org, one writer, the target's own validator pinned by
commit, one passing document from a published model on production, the README as the essay in four parts. No issues
are filed on the target's repositories (Tim, 9 October). Order of the track so far: CDIF, DCAT-US 3.0, now DCAT-AP;
HealthDCAT-AP is scoped here as a second phase; schema.org Dataset and Croissant follow.

## 1. Facts

**What DCAT-AP is.** The DCAT Application Profile for data portals in Europe: "a DCAT profile for sharing information
about Catalogues containing Datasets and Data Services descriptions in Europe," maintained by the SEMIC action of
Interoperable Europe (European Commission, DG DIGIT), originally a joint initiative of DG CONNECT, the Publications
Office and the ISA² programme. Its use case is cross-portal search: the exchange of dataset descriptions between data
portals (data.europa.eu harvests national portals in it). **DCAT-AP 3.0.1 is the current SEMIC Recommendation**, a
profile of W3C DCAT 3; a draft 3.0.2 is in progress. Specification: https://semiceu.github.io/DCAT-AP/releases/3.0.1/.
Tim's pointer: the SEMIC Support Centre release page (release 301). A separate annex, DCAT-AP HVD 3.0.0, covers the
high-value datasets of the Open Data Directive's implementing regulation; it is out of scope here (our sample is not
a European high-value dataset).

**Its shape.** RDF, validated by SHACL. A `dcat:Catalog` holds `dcat:Dataset`s (and `dcat:DataService`s), each
Dataset has `dcat:Distribution`s. Serialization is any RDF syntax; the Interoperability Test Bed accepts Turtle,
JSON-LD, RDF/XML and N-Triples, and the release ships a JSON-LD context (`context/dcat-ap.jsonld`). This is the first
target in the track that is RDF end to end: CDIF was JSON-LD framed for JSON Schema, DCAT-US is JSON Schema only.

**Mandatory properties** (from the release's `shacl/dcat-ap-SHACL.ttl`, `sh:minCount 1`):
| Class | Mandatory | Recommended (from the specification) |
|---|---|---|
| `dcat:Catalog` | `dct:title`, `dct:description`, `dct:publisher` | `dcat:dataset`, `dct:spatial`, `foaf:homepage`, `dct:language`, `dct:license`, `dct:modified`, `dct:issued`, `dcat:service`, `dcat:themeTaxonomy` |
| `dcat:Dataset` | `dct:title`, `dct:description` | `dcat:contactPoint`, `dcat:distribution`, `dct:spatial`, `dcat:keyword`, `dct:publisher`, `dct:temporal`, `dcat:theme` |
| `dcat:Distribution` | `dcat:accessURL` | `dcatap:availability`, `dct:description`, `dct:format`, `dct:license` |
| `foaf:Agent` | `foaf:name` | `dct:type` |
| `dcat:CatalogRecord` | `dct:modified`, `foaf:primaryTopic` | |
| `spdx:Checksum` | `spdx:algorithm`, `spdx:checksumValue` | |
| `adms:Identifier` | `skos:notation` | |

**Ranges** (`shacl/ranges.ttl`): every object property names a class its value must be an instance of (`dct:publisher`
a `foaf:Agent`, `dct:license` a `dct:LicenseDocument`, `dcat:theme` a `skos:Concept`, `dct:spatial` a `dct:Location`,
`dct:conformsTo` a `dct:Standard`, `dcat:contactPoint` a `vcard:Kind`, `dcat:landingPage` and `foaf:page` a
`foaf:Document`, `dct:language` a `dct:LinguisticSystem`, `dct:accessRights` a `dct:RightsStatement`, and so on).
A value referenced by URI alone, without a type triple in the graph, fails the ranges check; SEMIC's own minimal
example fails it for exactly that reason (section 4, part 4).

**Controlled vocabularies** the profile requires (the specification's table): `dcat:theme` from the EU Data Theme
vocabulary (`http://publications.europa.eu/resource/authority/data-theme/`), `dct:language` from the Languages Named
Authority List, `dct:format` from the File Type NAL, `dcat:mediaType` from IANA, `dct:accessRights` from the Access
Rights NAL, `dct:accrualPeriodicity` from the Frequency NAL, `dct:publisher` from the Corporate Bodies NAL (a
restriction a non-EU publisher cannot meet; the validator reports it as a warning), `dct:type` of an Agent from the
ADMS publisher-type vocabulary, `dct:spatial` from the Continents, Countries and Places NALs or Geonames.

**Validation.** Two judges.
1. **Local, offline, at the pin:** the release's two shape files run with pySHACL. They correspond to the ITB's
   "Base Zero" and "Ranges Zero" validation types ("no background knowledge": nothing fetched from the web).
2. **The Interoperability Test Bed's SEMIC SHACL validator**, https://www.itb.ec.europa.eu/shacl/dcat-ap/upload, with
   a REST API (`POST https://www.itb.ec.europa.eu/shacl/dcat-ap/api/validate`, JSON body with the content as a string,
   its syntax, a validation type and the report syntax; the report is a SHACL `sh:ValidationReport`). Validation types
   for 3.0.1: `base0`, `range0`, `base`, `range`, `codelists`, `rec`, `full`, `full1`; the ones "with background
   knowledge" load the EU vocabularies and dereference what the document references. The judge for the README is
   **`dcatap.3_0_1_full`: `sh:conforms true`, zero `sh:Violation`**, with the warnings it raises listed in part 4.
   Verified 9 October on SEMIC's own minimal example (`example-bee-population-2022-2023.ttl`): `base0` conforms;
   `range0` fails (the publisher is a bare URI, not typed `foaf:Agent`); `base` fails (no `foaf:name` found for it);
   `codelists` conforms with two warnings (the publisher is not in the Corporate Bodies NAL); `rec` conforms with
   eighteen warnings; `full` does not conform. A document that passes `full` has to carry its agents typed and
   named inline and its codelist values from the NALs.
   The codelist and recommendation shapes are the ITB's own (ISAITB `validator-resources-dcat-ap`), not in the SEMIC
   release; they are reached through the API, not pinned locally.

**Sources, pinned 9 October 2026.** `github.com/SEMICeu/DCAT-AP` at **4470b8e** (2026-06-16; CC BY 4.0, © European
Union), `releases/3.0.1/`: `shacl/dcat-ap-SHACL.ttl`, `shacl/ranges.ttl`, `context/dcat-ap.jsonld`,
`html/examples/`, `CHANGELOG.md`. Cloned read-only into `source/` (gitignored); `build/snapshot_dcat_ap.py` verifies
the pin and copies those into `data/dcat-ap-3.0.1-4470b8e/`. The ITB validator version is recorded from its
`/api/info` at run time (v1.14.0-SNAPSHOT on 9 October) in the README beside the result.

**HealthDCAT-AP** (phase 2). The European Health Data Space extension of DCAT-AP, moved from GitHub to the
Commission's infrastructure: specification at https://data.health.europa.eu/healthdcat-ap/releases/latest/,
repository https://code.europa.eu/healthdataeu/healthdcat-ap (CC BY 4.0, last activity 8 October 2026), releases 5
through 8 published, Release 8 dated September 2026. Each release ships `shacl/dcat-ap-SHACL.ttl` and
`shacl/ranges.ttl` of its own, so the same local judge applies; no ITB validation domain for it was found. It is the
EHDS pilot conversation (Tito Castillo, "Findable Is Not the Same as Usable"), and it is where typed missingness and
the per-record schema have a health audience; it comes after the base profile passes.

**How DCAT-AP relates to SDC: compose, not compete, as with the other two.** DCAT-AP describes a dataset for a
portal. SDC governs each record. DCAT-AP has no data-dictionary slot of its own (DCAT-US's `describedBy` has no
counterpart); the schema is cited as the standard the records conform to (`dct:conformsTo`, a `dct:Standard`) and
as a document about the dataset (`foaf:page`, a `foaf:Document`), both by URL with the SHA-256.

## 2. Rules

**One deliverable: the writer.** From a published SDC model's package, a DCAT-AP 3.0.1 Catalog in Turtle and in
JSON-LD (the same graph, two serializations, rdflib), one Dataset per model, passing the local shapes and the ITB
`full` validation. The seven FAIR Data Demo models as one Catalog is the same writer over a list.

**Two kinds of input, kept apart,** as in the DCAT-US writer. From the package: title, description, identifier,
creator, publisher when the modeler wrote `dc:publisher`, subject keywords, contributors, coverage, dates, language,
licence, the schema's URL and SHA-256. Declared by the catalog's publisher in `catalog.yaml`, because the profile's
controlled vocabularies and the ranges demand values the package cannot know: the publisher's `dct:type` (ADMS
publisher type), the contact point (`vcard:fn`, `vcard:hasEmail`; the track's convention: "Axius SDC, Inc. DCAT-AP
contact", `contact@axius-sdc.com`), the catalog's title, description and homepage, the EU data theme per model
(`HEAL` for the sample), `dct:accessRights` (`PUBLIC` from the Access Rights NAL), the language (`ENG` from the
Languages NAL). The README's part 3 says which fields came from the declared file.

**Mapping (the writer's rulebook):**
| SDC (package) | DCAT-AP 3.0.1 |
|---|---|
| Published model `dm-<ct>` | `dcat:Dataset` with `@id` the public catalog URL; `dct:identifier` `"dm-<ct>"`; `adms:identifier` an `adms:Identifier` with `skos:notation` `dm-<ct>` and `adms:schemaAgency` the publisher |
| Title, description | `dct:title`, `dct:description`, language-tagged `@en` |
| The published schema `/dmlib/dm-<ct>.xsd?sha256=` | `dct:conformsTo` a `dct:Standard` (`dct:title`, `dct:issued`, `dct:identifier` the SHA-256) **and** `foaf:page` a `foaf:Document` (`dct:title`, `dct:format` from the File Type NAL, `dct:description` naming it the data dictionary) |
| `dc:date` | `dct:issued`, `dct:modified` (`xsd:date`) |
| `dc:language` `en-US` | `dct:language` `<http://publications.europa.eu/resource/authority/language/ENG>` (from the declared input; the package's BCP 47 tag has no place in the NAL) |
| `dc:rights` with a URL | `dct:license` a `dct:LicenseDocument`; the remainder a `dct:rights` `dct:RightsStatement` with `rdfs:label` |
| `dc:creator` | `dct:creator` a `foaf:Agent` with `foaf:name` |
| `dc:publisher` or the declared publisher | `dct:publisher` a `foaf:Agent` with `foaf:name`, `dct:type` from ADMS, `foaf:homepage`; the same agent on the Catalog |
| `dc:subject` (semicolon list), project | `dcat:keyword` literals |
| `dc:coverage` when authored | `dct:spatial` a `dct:Location` with `skos:prefLabel` (a name; no geometry in the package) |
| Contributors | `dct:contributor` `foaf:Agent`s (DCAT 3 allows it on a Dataset; DCAT-AP lists it as optional) |
| Immutability | `dct:provenance` a `dct:ProvenanceStatement` with `rdfs:label`: a published model never changes, a revision is a new model naming the one it revised; and `dcat:version` the SHA-256 |
| Public catalog URL | `dcat:landingPage` a `foaf:Document` |
| Declared input | `dcat:contactPoint` a `vcard:Kind`; `dcat:theme` a `skos:Concept` from the Data Theme NAL; `dct:accessRights`; the Catalog's `dct:title`, `dct:description`, `foaf:homepage`, `dct:publisher` |
| The records themselves | `dcat:distribution`: omitted on the sample (not public; recommended, not mandatory, so a warning in `rec`), emitted when the declared input gives an access URL |

**Every referenced node is typed and named inline** (agents, documents, standards, concepts, licence documents): the
ranges check and the ITB's `base` validation require it, and a portal harvesting the catalog gets a complete graph.

**Not here.** DCAT-AP HVD; `dcat:DataService`; dataset series; the draft 3.0.2; the 3.0.1 JSON-LD context as our
output context (we serialize from the graph with full IRIs and standard prefixes, and let their context stay theirs).

**Attribution.** CC BY 4.0, © European Union: a NOTICE naming SEMIC and Interoperable Europe, the pinned commit in
`data/`.

**No issues filed** on SEMIC's repositories (Tim, 9 October). Part 4 carries how the artifacts behave, inside their
scope and not defects.

## 3. Scope

### 3.1 First: one model, the same record as the other two
- NHANES Participant (`xy8upneajsb8vdcmnve01g6g`, FAIR Data Demo), the same package, so the capstone's matrix keeps
  one record in every row.
- A Catalog with one Dataset, in Turtle and JSON-LD, passing the local shapes (base and ranges) with pySHACL and the
  ITB `full` validation with zero violations; the warnings listed.
- The README in the four parts.

### 3.2 Second: HealthDCAT-AP
The same writer with the HealthDCAT-AP shapes (Release 8 pinned) and its additional mandatory properties, on the
same record. Its own PRD section when phase 1 is green.

### 3.3 Then
- The seven FAIR Data Demo models as one Catalog.
- Any published model (`--ct-id`).
- `dcat:distribution` when a publisher exposes records.

## 4. Decisions (proposed; open for Tim)
1. **Package name `sdcdcatap`**, repository `sdc_dcat3_ap`, the `sdc_cdif` layout; dev to main by pull request with
   merge commits; CI offline (local shapes), the ITB run by a test marked network that CI skips and the README records.
2. **Package loader and model reader copied from `sdcdcatus`** (third repository: the moment lane 5.6 named for
   lifting them into a shared package. Proposed: do the copy now, open the shared-package question after this one is
   green, so the third repository does not wait on a refactor).
3. **Output is Turtle and JSON-LD from one rdflib graph**, full IRIs with standard prefixes; the ITB validates both.
4. **Declared input carries the controlled-vocabulary values** the package cannot know: theme (`HEAL` for the sample),
   access rights (`PUBLIC`), language (`ENG`), publisher type (ADMS `Company`), contact ("Axius SDC, Inc. DCAT-AP
   contact", `contact@axius-sdc.com`).
5. **The schema fills `dct:conformsTo` and `foaf:page`**: the standard the records conform to, and the document that
   defines their variables. DCAT-AP has no data-dictionary slot; this is the nearest honest pair.
6. **The judge is the ITB `full` validation with zero violations**, warnings allowed and listed; the local shapes are
   the offline gate in CI.
7. **No `dcat:distribution` on the sample**, as in DCAT-US.

## 5. Pipeline
`source/` (SEMICeu/DCAT-AP at 4470b8e, read-only), then `build/snapshot_dcat_ap.py` (verify the pin; copy the
3.0.1 shapes, context, examples and changelog to `data/dcat-ap-3.0.1-4470b8e/`), then `src/sdcdcatap/` (`package.py`
and `model.py` from `sdcdcatus`; `dcatap.py` builds the graph; `cli.py`: `sdcdcatap write --package DIR [--catalog
catalog.yaml] --out catalog.ttl [--jsonld catalog.jsonld]`), then `tests/` (pySHACL with the pinned shapes against
our output and against SEMIC's own examples as a sanity check; an ITB test behind a network marker), then the README.

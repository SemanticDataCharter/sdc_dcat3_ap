# sdc_dcat3_ap

One Semantic Data Charter model, described in DCAT-AP 3.0.1.

`sdcdcatap` reads a published SDC model's package and writes the `dcat:Catalog` that DCAT-AP, the DCAT Application
Profile for data portals in Europe, asks a portal to exchange: one Dataset per model, the model's schema cited as
the standard its records conform to (`dct:conformsTo`) and as the document that defines their variables
(`foaf:page`), by URL and SHA-256. One rdflib graph, serialized as Turtle and as JSON-LD. The output is checked with
SEMIC's own SHACL shapes at a pinned commit and with the Interoperability Test Bed's SEMIC validator.

## 1. What this is, and where it came from

The sample, `samples/nhanes-participant/catalog.ttl` (and `catalog.jsonld`, the same graph), is a Catalog with one
Dataset: the records of **NHANES Participant** (`dm-xy8upneajsb8vdcmnve01g6g`) from the FAIR Data Demo, a
demographic, examination and laboratory record of the National Health and Nutrition Examination Survey (CDC). The
model is public:

- the catalog record: https://sdcstudio.axius-sdc.com/api/v1/catalog/dm/xy8upneajsb8vdcmnve01g6g/
- the schema the records conform to: https://sdcstudio.axius-sdc.com/dmlib/dm-xy8upneajsb8vdcmnve01g6g.xsd
- the Semantic Data Charter: https://semanticdatacharter.com

```
pip install -e ".[fetch]"
sdcdcatap write --package samples/nhanes-participant --out catalog.ttl --jsonld catalog.jsonld
sdcdcatap write --ct-id xy8upneajsb8vdcmnve01g6g --ct-id <another> --save-package pkg/ --out catalog.ttl   # a catalog of models, from the public catalog
sdcdcatap write --package DIR --catalog my-catalog.yaml --out catalog.ttl                                  # a publisher's own declared input
```

**Two kinds of input, kept apart.** From the model's package (its JSON-LD, its schema, the public catalog record and
the published schema versions; no account needed; a model without a package is refused): title, description,
identifier, creator, dates, licence, the schema's URL and SHA-256, the variable count, and the model's own Dublin
Core when the modeler wrote it (publisher, subject keywords, contributors, coverage). From the catalog's publisher,
declared in `catalog.yaml` because the profile's controlled vocabularies and range rules demand values the package
cannot know: the contact point, the EU data theme, access rights, language, the publisher's ADMS type, the catalog's
own title, description and homepage. The package ships a default file for the sample
(`src/sdcdcatap/data/catalog.yaml`); a publisher supplies its own.

**Every referenced node is typed and named inline.** The range shapes require every object value to be an instance
of its class, and the mandatory shapes require a name on every agent and a label on every concept, wherever they
sit in the graph. So the publisher is a `foaf:Agent` with a `foaf:name`, the theme is a `skos:Concept` with a
`skos:prefLabel` in its scheme, the licence is a `dct:LicenseDocument`, the language a `dct:LinguisticSystem`, and so
on. A harvesting portal gets a complete graph.

What the Dataset carries:

| | |
|---|---|
| `dct:title`, `dct:description` | the model's, English-tagged, plus one sentence saying what a governed data record is and that the schema is immutable |
| `dct:identifier`, `adms:identifier` | `dm-xy8upneajsb8vdcmnve01g6g`, as a literal and as an `adms:Identifier` with `skos:notation` |
| `dct:conformsTo` | a `dct:Standard`: the schema at its pinned URL (`?sha256=`), with the SHA-256 as `dct:identifier` |
| `foaf:page` | a `foaf:Document`: the schema at its stable URL, described as the data dictionary (153 variables), `dct:format` XML from the File Type NAL, itself `dct:conformsTo` the SDC4 reference model |
| `dct:publisher`, `dct:creator` | `foaf:Agent`s with names; the publisher with its ADMS type and homepage |
| `dcat:contactPoint` | a `vcard:Kind` with `vcard:fn` and `vcard:hasEmail`, from the declared input |
| `dcat:theme`, `dct:language`, `dct:accessRights` | `HEAL` from the EU Data Theme vocabulary, `ENG` from the Languages NAL, `PUBLIC` from the Access Rights NAL, from the declared input |
| `dct:license` | the model's licence URL as a `dct:LicenseDocument` |
| `dcat:keyword`, `dcat:landingPage`, `dct:issued`, `dct:modified` | from the package |
| `dct:provenance`, `dcat:version` | a `dct:ProvenanceStatement`: a published model never changes, a revision is a new model naming the one it revised; the SHA-256 as the version |

The Catalog carries its title, description, publisher, homepage, language, dates, the Data Theme vocabulary as
`dcat:themeTaxonomy`, and the Dataset.

## 2. How to verify it

The tests run SEMIC's shapes from `data/dcat-ap-3.0.1-4470b8e/`, copied at the pinned commit
(`build/snapshot_dcat_ap.py` verifies the pin first), with pySHACL:

```
pip install -e ".[dev]"
python -m pytest tests -q                   # the Interoperability Test Bed test runs too, over the network
python -m pytest tests -q -m "not network"  # offline, as CI runs it
```

Offline: the mandatory-property shapes (`dcat-ap-SHACL.ttl`) and the range shapes (`ranges.ttl`), both `conforms`,
in Turtle and in JSON-LD. The committed samples are asserted isomorphic to a fresh run.

The second judge, the Interoperability Test Bed's SEMIC SHACL validator (https://www.itb.ec.europa.eu/shacl/dcat-ap/,
v1.14.0-SNAPSHOT on 9 October 2026, through its REST API), on the sample:

| Validation type | Result |
|---|---|
| `dcatap.3_0_1_base0` (mandatory, no background knowledge) | conforms |
| `dcatap.3_0_1_range0` (ranges, no background knowledge) | conforms |
| `dcatap.3_0_1_codelists` (controlled vocabularies) | conforms, 3 warnings: the publisher is not in the EU Corporate Bodies NAL (it is a company, not an EU body) |
| `dcatap.3_0_1_rec` (recommendations) | conforms, 19 warnings, listed in part 4 |
| `dcatap.3_0_1_full` (everything, with background knowledge) | 11 violations that are not in the document: see part 4 |

The network test asserts the first four.

## 3. What the projection could not say

Left out rather than filled in:
- **No `dcat:distribution` of the records.** The FAIR Data Demo's records are not published; the model is. The
  profile recommends a distribution and does not require one; the writer emits one when a publisher declares an
  access URL.
- **No temporal coverage, no geometry, no frequency, no dataset series, no data service.** The package does not
  carry them. Spatial coverage, subject keywords, contributors and the model's own publisher come from the model's
  Dublin Core when the modeler wrote them; SDCStudio's field defaults ("Universal" for coverage, "None" for relation,
  blanks) read as unset, which is why the NHANES catalog carries none of them.
- **Nothing a publisher would have to decide.** The data theme, access rights, language, the publisher's type and
  the contact point are declared input, said so here, and defaulted only for the sample.

In the other direction, what the record carries that a catalog entry has no place for, stated so a reader knows
where to look rather than as a shortcoming of either side:
- **The governance envelope is data in every record.** Each Governed Data Record carries its own audit event, PROV
  activity and PROV agent as validated leaves. DCAT-AP's `dct:provenance` and `prov:wasGeneratedBy` describe the
  dataset; the per-record facts are in the records, defined in the schema the catalog points at.
- **The schema is bound to each record.** Every record names the schema it was validated against; the catalog says
  that once, in `dct:conformsTo` with the SHA-256.
- **The reason a value is missing is typed in the record.** A leaf may carry one of sixteen exceptional values in
  place of its value; the schema defines them; which one applies, and where, is in the record.
- **There is no data-dictionary slot.** DCAT-US 3.0 has `describedBy` for "the names and definitions of all
  variables"; DCAT-AP has `dct:conformsTo` and `foaf:page`, which is where the schema goes here.

## 4. What we learned about DCAT-AP 3.0.1 and its validators

Implementer's notes from building this against `SEMICeu/DCAT-AP` at 4470b8e and the Interoperability Test Bed on
9 October 2026. They describe how the artifacts behave, so the next implementer spends the day on their own catalog
rather than on these.

- **Type and name everything you reference.** The ranges file checks `sh:class` on every object property, and the
  base file requires `foaf:name` on every `foaf:Agent` and `skos:prefLabel` on every `skos:Concept` in the graph,
  including vocabulary terms you merely point at (the ADMS publisher type, the data theme). SEMIC's own minimal
  example, with its publisher as a bare URI, passes the mandatory shapes and fails the ranges for exactly this
  reason.
- **The `full` and `base` types report violations that are not in the document.** An empty minimal catalog (title,
  description, a named publisher) submitted to `dcatap.3_0_1_base` returns the same five `foaf:name` violations on
  blank-node agents as our sample does, and `full` adds six `dct:title` violations on ADMS concept schemes
  (`http://purl.org/adms/publishertype/1.0` and siblings). They come from the background knowledge those types load,
  not from the content. Read the four groups individually (`base0`, `range0`, `codelists`, `rec`), each of which
  reports only on the document; that is what the table in part 2 does.
- **The recommendations type treats the Catalog as a Dataset.** With DCAT loaded as background knowledge
  (`dcat:Catalog` is a subclass of `dcat:Dataset`), the Dataset recommendations fire on the Catalog too: contact
  point, distribution, keyword, theme, spatial and temporal coverage, licence. Of the 19 warnings on the sample,
  nine are those; the rest are the Dataset's missing distribution, spatial and temporal coverage, `dct:type` on the
  creator agent and on the licence document (ADMS licence type), and the publisher outside the Corporate Bodies NAL.
- **`ranges.ttl` references property shapes it does not define.** 206 `sh:property` triples point at nodes with no
  triples of their own. A Jena-based validator passes over them; pySHACL refuses to run ("not a well-formed SHACL
  PropertyShape"). The tests drop the undefined references before running; the 91 defined property shapes are what
  is checked.
- **The REST API is simple.** `POST https://www.itb.ec.europa.eu/shacl/dcat-ap/api/validate` with a JSON body of
  `contentToValidate` (the document as a string), `embeddingMethod: STRING`, `contentSyntax`, `validationType` and
  `reportSyntax`; the answer is a SHACL validation report. `/api/info` lists the validation types and the validator
  version. JSON-LD and Turtle gave identical results.
- **`dcat:version` is a DCAT 3 property that rdflib's closed `DCAT` namespace does not know**; build the IRI by hand.
- **The language is a NAL concept, not a tag.** `dct:language` takes `http://publications.europa.eu/resource/authority/language/ENG`,
  a `dct:LinguisticSystem`; a BCP 47 string fails the ranges.

## Layout

- The model's package is read with [`sdcreader`](https://github.com/SemanticDataCharter/sdcreader) (`load_package`,
  `fetch_package`, `read_model`): the record tree, its leaves, the enumerated values with their codes, the model's
  Dublin Core with SDCStudio's defaults as unset. The package format is documented there, once.
- `src/sdcdcatap/`: `dcatap.py` (the graph), `cli.py`, `data/catalog.yaml` (the declared input for the sample).
- `data/dcat-ap-3.0.1-4470b8e/`: SEMIC's shapes, context, examples and changelog at the pin.
- `samples/nhanes-participant/`: the model's package as fetched and the catalog written from it, in Turtle and JSON-LD.
- `build/snapshot_dcat_ap.py`: re-creates `data/` from a read-only clone of `SEMICeu/DCAT-AP` at the pinned commit.

## Licences

Apache-2.0 (see `LICENSE`, `NOTICE`). The DCAT-AP artifacts in `data/` are © European Union, CC BY 4.0, and keep that
licence here.

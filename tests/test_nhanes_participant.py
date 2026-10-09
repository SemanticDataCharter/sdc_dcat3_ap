"""The NHANES Participant catalog passes SEMIC's DCAT-AP 3.0.1 shapes at the pinned commit (the mandatory-property
shapes and the range shapes, with pySHACL), in Turtle and in JSON-LD; SEMIC's own example behaves at the pin as
recorded; the schema is cited as the standard and as the page by URL and SHA-256; and the writer says only what the
package and the declared input say. The Interoperability Test Bed is the second judge, behind the network marker."""
import hashlib
import json
from datetime import date
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, SKOS

from sdcdcatap import DeclaredInputError, build_catalog, load_declared, load_package, read_model

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "samples" / "nhanes-participant"
SNAPSHOT = ROOT / "data" / "dcat-ap-3.0.1-4470b8e"
SH = Namespace("http://www.w3.org/ns/shacl#")
CT = "xy8upneajsb8vdcmnve01g6g"
DAY = date(2026, 10, 9)
DS = URIRef(f"https://semanticdatacharter.com/ns/sdc4/dm-{CT}")


def shapes(name: str) -> Graph:
    g = Graph().parse(SNAPSHOT / "shacl" / name, format="turtle")
    if name == "ranges.ttl":
        # the file lists property shapes it does not define; a Jena-based validator passes over them, pySHACL stops
        for t in [t for t in g.triples((None, SH.property, None)) if (t[2], None, None) not in g]:
            g.remove(t)
    return g


@pytest.fixture(scope="module")
def base():
    return shapes("dcat-ap-SHACL.ttl")


@pytest.fixture(scope="module")
def ranges():
    return shapes("ranges.ttl")


@pytest.fixture(scope="module")
def model():
    return read_model(load_package(PACKAGE))


@pytest.fixture(scope="module")
def graph(model):
    return build_catalog([model], load_declared(), today=DAY)


def results(data: Graph, sg: Graph):
    ok, rg, _ = validate(data, shacl_graph=sg, inference="none")
    return ok, sorted(f"{rg.value(r, SH.resultSeverity).split('#')[1]} {rg.value(r, SH.focusNode)} {rg.value(r, SH.resultPath)}: {rg.value(r, SH.resultMessage)}"
                      for r in rg.subjects(RDF.type, SH.ValidationResult))


def test_the_catalog_passes_the_mandatory_and_range_shapes_in_turtle_and_json_ld(graph, base, ranges):
    for fmt in ("turtle", "json-ld"):
        data = Graph().parse(data=graph.serialize(format=fmt), format=fmt)
        for sg in (base, ranges):
            ok, errs = results(data, sg)
            assert ok, (fmt, errs[:5])


def test_the_committed_samples_equal_a_fresh_run(graph):
    for name, fmt in (("catalog.ttl", "turtle"), ("catalog.jsonld", "json-ld")):
        committed = Graph().parse(PACKAGE / name, format=fmt)
        assert committed.isomorphic(graph), name


def test_semic_s_own_example_behaves_at_the_pin_as_recorded(base, ranges):
    """Their minimal example passes the mandatory shapes and fails the ranges: its publisher is a bare URI with no type."""
    ex = Graph().parse(SNAPSHOT / "examples" / "example-bee-population-2022-2023.ttl", format="turtle")
    ok, _ = results(ex, base)
    # pySHACL applies sh:class on the base shapes too, so both report the untyped publisher
    ok2, errs = results(ex, ranges)
    assert not ok2 and all("foaf:Agent" in e for e in errs) and len(errs) == 2, errs


def test_the_schema_is_the_standard_and_the_page_by_url_and_sha256(graph, model):
    sha = hashlib.sha256((PACKAGE / f"dm-{CT}.xsd").read_bytes()).hexdigest()
    assert model.package.sha256 == sha == model.package.versions["current_sha256"]
    pinned = URIRef(f"https://sdcstudio.axius-sdc.com/dmlib/dm-{CT}.xsd?sha256={sha}")
    assert (DS, DCTERMS.conformsTo, pinned) in graph and (pinned, RDF.type, DCTERMS.Standard) in graph
    assert str(graph.value(pinned, DCTERMS.identifier)) == f"sha256:{sha}"
    page = URIRef(f"https://sdcstudio.axius-sdc.com/dmlib/dm-{CT}.xsd")
    assert (DS, FOAF.page, page) in graph and (page, RDF.type, FOAF.Document) in graph
    assert "153 variables" in str(graph.value(page, DCTERMS.description))
    assert str(graph.value(DS, DCTERMS.identifier)) == f"dm-{CT}"
    assert (DS, DCAT.distribution, None) not in graph   # the records are not public; stated in the README


def test_every_referenced_node_is_typed_and_named(graph):
    for agent in graph.objects(None, DCTERMS.publisher):
        assert (agent, RDF.type, FOAF.Agent) in graph and (agent, FOAF.name, None) in graph
    for concept in graph.subjects(RDF.type, SKOS.Concept):
        assert (concept, SKOS.prefLabel, None) in graph, concept
    theme = URIRef("http://publications.europa.eu/resource/authority/data-theme/HEAL")
    assert (DS, DCAT.theme, theme) in graph
    assert (DS, DCTERMS.language, URIRef("http://publications.europa.eu/resource/authority/language/ENG")) in graph
    assert (DS, DCTERMS.accessRights, URIRef("http://publications.europa.eu/resource/authority/access-right/PUBLIC")) in graph


def test_the_contact_point_and_vocabulary_values_are_declared_input(graph):
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    kind = graph.value(DS, DCAT.contactPoint)
    assert str(graph.value(kind, VCARD.fn)) == "Axius SDC, Inc. DCAT-AP contact"
    assert str(graph.value(kind, VCARD.hasEmail)) == "mailto:contact@axius-sdc.com"
    with pytest.raises(DeclaredInputError, match="contact e-mail"):
        load_declared(None, None, "not-an-address")


def test_the_models_dublin_core_is_read_with_defaults_as_unset(model, graph):
    assert model.header["coverage"] == "Universal" and model.dc("coverage") is None
    assert (DS, DCTERMS.spatial, None) not in graph
    import copy
    authored = copy.copy(model)
    authored.header = dict(model.header, publisher="National Center for Health Statistics", subject="blood pressure; NHANES",
                           coverage="United States, civilian noninstitutionalized population", contributor=["A. Modeler"])
    g2 = build_catalog([authored], load_declared(), today=DAY)
    pub = g2.value(DS, DCTERMS.publisher)
    assert str(g2.value(pub, FOAF.name)) == "National Center for Health Statistics"
    assert (DS, DCTERMS.spatial, None) in g2 and (DS, DCTERMS.contributor, None) in g2
    assert any(str(k) == "blood pressure" for k in g2.objects(DS, DCAT.keyword))
    for sg in (shapes("dcat-ap-SHACL.ttl"), shapes("ranges.ttl")):
        ok, errs = results(g2, sg)
        assert ok, errs[:5]


@pytest.mark.network
def test_the_interoperability_test_bed_agrees(graph):
    """The ITB's four groups without background knowledge: base0 and range0 conform; codelists and rec conform with warnings."""
    import urllib.request
    ttl = graph.serialize(format="turtle")
    for vt, expect_warnings in (("dcatap.3_0_1_base0", False), ("dcatap.3_0_1_range0", False), ("dcatap.3_0_1_codelists", True), ("dcatap.3_0_1_rec", True)):
        body = {"contentToValidate": ttl, "embeddingMethod": "STRING", "contentSyntax": "text/turtle", "validationType": vt, "reportSyntax": "application/ld+json"}
        req = urllib.request.Request("https://www.itb.ec.europa.eu/shacl/dcat-ap/api/validate", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "Accept": "application/ld+json"})
        d = json.loads(urllib.request.urlopen(req, timeout=180).read().decode())
        nodes = d.get("@graph", [d])
        conforms = next(n["sh:conforms"]["@value"] for n in nodes if "sh:conforms" in n)
        violations = [n for n in nodes if n.get("@type") == "sh:ValidationResult" and n["sh:resultSeverity"]["@id"] == "sh:Violation"]
        assert conforms == "true" and not violations, (vt, violations[:3])

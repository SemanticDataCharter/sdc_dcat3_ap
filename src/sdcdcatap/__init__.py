"""Describe a published Semantic Data Charter model's governed data records in DCAT-AP 3.0.1.

One or more models in, one dcat:Catalog out (an rdflib graph, serialized as Turtle or JSON-LD): a Dataset per model,
its schema cited as the standard the records conform to (dct:conformsTo) and as the document that defines their
variables (foaf:page), by URL and SHA-256. Validated with SEMIC's own SHACL shapes at a pinned commit and with the
Interoperability Test Bed's validator.
"""
from sdcreader import ModelPackage, load_package, fetch_package, read_model
from .dcatap import build_catalog, load_declared, DeclaredInputError

__version__ = "4.0.0"
__all__ = ["ModelPackage", "load_package", "fetch_package", "read_model", "build_catalog", "load_declared", "DeclaredInputError", "__version__"]

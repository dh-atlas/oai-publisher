from flask import Response, jsonify
from datetime import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

OAI_NS = "http://www.openarchives.org/OAI/2.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
BASE_URL = "http://localhost:5000/oai"

class OAI_PMH_Error(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)


def create_base_response(verb):
    root = ET.Element(f"{{{OAI_NS}}}OAI-PMH")
    root.set(f"{{{XSI_NS}}}schemaLocation",
             "http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd")

    ET.SubElement(root, f"{{{OAI_NS}}}responseDate").text = datetime.utcnow().isoformat() + "Z"
    req = ET.SubElement(root, f"{{{OAI_NS}}}request")
    req.set("verb", verb)
    req.text = BASE_URL
    return root


def to_pretty_xml(root):
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    return Response(pretty_xml, mimetype="text/xml")


def to_json_response(data):
    return jsonify(data)


def handle_oai_error(error):
    root = create_base_response("error")
    e = ET.SubElement(root, f"{{{OAI_NS}}}error")
    e.set("code", error.code)
    e.text = error.message
    return to_pretty_xml(root)


from flask import Flask, request
from handlers import (
    handler_identify,
    handler_list_identifiers,
    handler_list_records,
    handler_get_record,
    list_metadata_formats
)
from raw_handlers import (
    raw_handler_identify,
    raw_handler_list_identifiers,
    raw_handler_list_records,
    raw_handler_get_record,
    raw_list_metadata_formats
)
from response import handle_oai_error, OAI_PMH_Error

app = Flask(__name__)


@app.route("/oai")
def oai():
    try:
        verb = request.args.get("verb")
        if not verb:
            raise OAI_PMH_Error("badVerb", "Missing verb parameter")

        if verb == "Identify":
            return handler_identify()
        elif verb == "ListIdentifiers":
            return handler_list_identifiers(request.args)
        elif verb == "ListRecords":
            metadataPrefix=request.args.get("metadataPrefix")
            return handler_list_records(metadataPrefix)
        elif verb == "ListMetadataFormats":
            return list_metadata_formats(request.args)
			            
        elif verb == "GetRecord":
            identifier = request.args.get("identifier")
            metadataPrefix=request.args.get("metadataPrefix")
                
            if not identifier:
                raise OAI_PMH_Error("badArgument", "Missing identifier parameter for GetRecord")
            return handler_get_record(identifier,metadataPrefix)
        raise OAI_PMH_Error("badVerb", f"Unsupported verb: {verb}")
    except OAI_PMH_Error as e:
        return handle_oai_error(e)


@app.route("/oai_raw")
def oai_raw():
    try:
        verb = request.args.get("verb")
        if not verb:
            raise OAI_PMH_Error("badVerb", "Missing verb parameter")

        if verb == "Identify":
            return raw_handler_identify()
        elif verb == "ListIdentifiers":
            return raw_handler_list_identifiers(request.args)
        elif verb == "ListMetadataFormats":
            return raw_list_metadata_formats(request.args)
        elif verb == "ListRecords":
            return raw_handler_list_records(request.args)
        elif verb == "GetRecord":
            identifier = request.args.get("identifier")
            if not identifier:
                raise OAI_PMH_Error("badArgument", "Missing identifier parameter for GetRecord")
            return raw_handler_get_record(identifier)

        raise OAI_PMH_Error("badVerb", f"Unsupported verb: {verb}")
    except OAI_PMH_Error as e:
        return handle_oai_error(e)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

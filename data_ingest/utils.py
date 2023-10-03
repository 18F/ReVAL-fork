import csv
import json
import io
import logging
from collections import OrderedDict
from django.utils.module_loading import import_string
from .ingest_settings import UPLOAD_SETTINGS

logger = logging.getLogger("ReVAL")


def get_schema_headers():
    ordered_header = []

    good_table_validator = "data_ingest.ingestors.GoodtablesValidator"
    schema = [
        loc
        for loc, val_type in UPLOAD_SETTINGS["VALIDATORS"].items()
        if val_type == good_table_validator and loc is not None
    ]
    if schema:
        validator = import_string(good_table_validator)(
            name=good_table_validator, filename=schema[0]
        )
        contents = validator.get_validator_contents()
        ordered_header = [field["name"] for field in contents.get("fields", [])]
    return ordered_header


def get_ordered_headers(headers):
    if isinstance(UPLOAD_SETTINGS["STREAM_ARGS"]["headers"], list):
        return UPLOAD_SETTINGS["STREAM_ARGS"]["headers"]

    correct_headers = get_schema_headers()
    if correct_headers == headers:
        return headers

    working_headers = headers.copy()
    o_headers = []
    for h in correct_headers:
        if h in working_headers:
            o_headers.append(h)
            working_headers.remove(h)
    # add back header that didn't exist in the schema but in headers
    o_headers.extend(working_headers)
    return o_headers


def process_row(row, headers):
    row_data = []
    for header in headers:
        logger.debug(f"Fetching: {header}")
        val = row.get(header, None)
        row_data.append(val)
        logger.debug(f"Set to: {val}")
    return row_data


def to_tabular(incoming):
    """Coerce incoming json to tabular structure for tabulator
    [
        [All observed keys(headers)],
        [values],
        [values],
        ...
    ]

    First list contains all observed `columns`, following lists
    are data rows containing data values in the order of headers defined
    in the first row.
    """
    if incoming is None:
        return incoming

    data = incoming.copy()

    # if we are going through the API, the JSONDecoder already
    # converts the source JSON to a python dictionary for us.
    jsonbuffer = None

    try:
        print("🐶")
        print(type(data))
        print(data)
        jsonbuffer = json.loads(data["source"].decode())
        print("🦁")
    except (TypeError, KeyError, AttributeError):
        print("🐯 ERROR")
        jsonbuffer = data.decode()["source"]

    headers = set()

    # If dict of values appear in a list, I assume there may be more than one dict of values
    # This should work with one or more values.
    for data_dict in jsonbuffer:
        print("🥸 ", data_dict)
        headers = headers.union(set(data_dict.keys()))
    o_headers = get_ordered_headers(headers)

    output = [o_headers]

    for data_dict in jsonbuffer:
        for row in data_dict:
            row_data = process_row(row, o_headers)
            output.append(row_data)

    return output


def reorder_csv(incoming):
    if incoming.get("source") is None:
        return incoming

    data = incoming.copy()

    csvbuffer = io.StringIO(data["source"].decode("UTF-8"))

    output = io.StringIO()
    headers = []
    header_mapping = {}
    writer = None
    # This will make sure empty lines are not deleted
    lines = ("," if line.isspace() else line for line in csvbuffer)

    for row in csv.DictReader(lines):
        if not headers:
            # write headers first
            headers = get_ordered_headers(list(row.keys()))
            writer = csv.DictWriter(
                output, fieldnames=headers, extrasaction="ignore", lineterminator="\n"
            )
            writer.writeheader()
            if isinstance(UPLOAD_SETTINGS["STREAM_ARGS"]["headers"], list):
                header_mapping = dict(zip(row.keys(), headers))
        # If there's extra item in the row
        if row.get(None):
            vals = [row.get(header, "") for header in headers]
            vals.extend(row.get(None))
            write_row = ",".join(vals)

            output.write(write_row + "\n")
        else:
            writer.writerow(
                OrderedDict([(header_mapping.get(k, k), v) for k, v in row.items()])
            )

    data["source"] = output.getvalue().encode("UTF-8")
    return data

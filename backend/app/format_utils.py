import csv
import io
import xml.etree.ElementTree as ET

from fastapi.responses import JSONResponse, Response


def listings_to_xml(data: list[dict], total: int = 0, page: int = 1) -> str:
    root = ET.Element("listings", total=str(total), page=str(page))
    for item in data:
        listing_el = ET.SubElement(root, "listing", id=str(item.get("otodom_id", "")))
        for key, value in item.items():
            if key == "otodom_id":
                continue
            child = ET.SubElement(listing_el, key)
            if key == "price":
                child.set("currency", "PLN")
            elif key == "area":
                child.set("unit", "m2")
            child.text = str(value) if value is not None else ""
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


def listings_to_csv(data: list[dict]) -> str:
    if not data:
        return ""
    output = io.StringIO()
    output.write("\ufeff")  # UTF-8 BOM for Excel
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def single_listing_to_xml(data: dict) -> str:
    root = ET.Element("listing", id=str(data.get("otodom_id", "")))
    for key, value in data.items():
        if key == "otodom_id":
            continue
        child = ET.SubElement(root, key)
        child.text = str(value) if value is not None else ""
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


async def format_response(data, fmt: str, filename: str, total: int = 0, page: int = 1):
    if isinstance(data, list):
        items = data
    else:
        items = [data]

    if fmt == "xml":
        if len(items) == 1 and not isinstance(data, list):
            xml = single_listing_to_xml(items[0])
        else:
            xml = listings_to_xml(items, total=total, page=page)
        return Response(xml, media_type="application/xml")
    elif fmt == "csv":
        csv_content = listings_to_csv(items)
        return Response(
            csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )
    else:
        return JSONResponse(data)

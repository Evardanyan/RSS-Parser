# You shouldn't change  name of function or their arguments
# but you can change content of the initial functions.
import json as JS
from argparse import ArgumentParser
from typing import List, Optional, Sequence
from xml.sax import saxutils

import requests
import xml.etree.ElementTree as ET


class UnhandledException(Exception):
    pass


def rss_parser(
        xml: str,
        limit: Optional[int] = None,
        json: bool = False,
) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to file as a separate lines.

    Examples:
        >>> xml = '<rss><channel><title>Some RSS Channel</title><link>https://some.rss.com</link><description>Some RSS Channel</description></channel></rss>'
        >>> rss_parser(xml)
        ["Feed: Some RSS Channel",
        "Link: https://some.rss.com"]
        >>> print("\\n".join(rss_parser(xmls)))
        Feed: Some RSS Channel
        Link: https://some.rss.com
    """

    # Your code goes here
    def parse_util(xml: str):
        root = ET.fromstring(xml)
        channel = root.find('channel')

        result = {}

        result_json = {}

        title = saxutils.unescape(channel.find("title").text) if channel.find("title") is not None else ""
        if title:
            result["Feed"] = title
            result_json["title"] = title

        link = saxutils.unescape(channel.find("link").text) if channel.find("link") is not None else ""
        if link:
            result["Link"] = link
            result_json["link"] = link

        last_build_date = saxutils.unescape(channel.find("lastBuildDate").text) if channel.find(
            "lastBuildDate") is not None else ""
        if last_build_date:
            result["Last Build Date"] = last_build_date
            result_json["lastBuildDate"] = last_build_date

        pub_date = saxutils.unescape(channel.find("pubDate").text) if channel.find("pubDate") is not None else ""
        if pub_date:
            result["Publish Date"] = pub_date
            result_json["pubDate"] = pub_date

        language = saxutils.unescape(channel.find("language").text) if channel.find("language") is not None else ""
        if language:
            result["Language"] = language
            result_json["language"] = language

        editor = saxutils.unescape(channel.find("managingEditor").text) if channel.find(
            "managingEditor") is not None else ""
        if editor:
            result["Editor"] = editor
            result_json["managingEditor"] = editor

        description = saxutils.unescape(channel.find("description").text) if channel.find(
            "description") is not None else ""
        if description:
            result["Description"] = description
            result_json["description"] = description

        categories = []
        for category in channel.findall("category"):
            categories.append(saxutils.unescape(category.text))
        if categories:
            result["Categories"] = categories
            result_json["category"] = categories

        items = []
        items_json = []

        for item in channel.findall("item"):
            item_data = {}
            item_data_json = {}

            title = saxutils.unescape(item.find("title").text) if item.find("title") is not None else ""
            if title:
                item_data["Title"] = title
                item_data_json["title"] = title

            author = saxutils.unescape(item.find("author").text) if item.find("author") is not None else ""
            if author:
                item_data["Author"] = author
                item_data_json["author"] = author

            published = saxutils.unescape(item.find("pubDate").text) if item.find("pubDate") is not None else ""
            if published:
                item_data["Published"] = published
                item_data_json["pubDate"] = published

            link = saxutils.unescape(item.find("link").text) if item.find("link") is not None else ""
            if link:
                item_data["Link"] = link
                item_data_json["link"] = link

            item_categories = []
            for category in item.findall("category"):
                item_categories.append(saxutils.unescape(category.text))
            if item_categories:
                item_data["Categories"] = item_categories
                item_data_json["category"] = item_categories

            description = saxutils.unescape(item.find("description").text) if item.find(
                "description") is not None else ""
            if description:
                item_data["Description"] = description
                item_data_json["description"] = description

            items.append(item_data)
            items_json.append((item_data_json))

        if items:
            result["Items"] = items
            result_json["items"] = items_json

        xml_list = [result, result_json]

        return xml_list

    def get_output(xml, limit: Optional[int] = None, is_json: bool = False):
        if is_json:
            xml = xml[1]
            if limit:
                xml['items'] = xml['items'][:limit]
                return [JS.dumps(xml, indent=2, ensure_ascii=False)]
            else:
                return [JS.dumps(xml, indent=2, ensure_ascii=False)]
        else:
            xml = xml[0]
            output = []
            keys = ["Feed", "Link", "Last Build Date", "Publish Date", "Language", "Editor", "Description"]
            for key in keys:
                if key in xml:
                    output.append(f"{key}: {xml[key]}")
            output.append("")

            if 'Items' in xml:
                items = xml["Items"]

                if limit:
                    items = items[:limit]

                if items:
                    for item in items:
                        item_keys = ["Title", "Author", "Published", "Link", "Categories", "Description"]
                        item_output = []
                        for item_key in item_keys:
                            if item_key in item:
                                if item_key == "Categories":
                                    item_output.append(f"{item_key}: {', '.join(item[item_key])}")
                                elif item_key == "Description":
                                    item_output.append(f"\n{item[item_key]}")
                                else:
                                    item_output.append(f"{item_key}: {item[item_key]}")
                        output.extend(item_output)
                        output.append("")
            return output

    return get_output(parse_util(xml), limit, json)


def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)
    xml = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()

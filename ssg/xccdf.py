"""
A couple generic XCCDF utilities used by build_all_guides.py and
build_all_remediations.py

Author: Martin Preisler <mpreisle@redhat.com>
"""

from __future__ import absolute_import
from __future__ import print_function

import re

from .constants import XCCDF12_NS

# if a profile ID ends with a string listed here we skip it
PROFILE_ID_SKIPLIST = ["test", "index", "default"]
# filler XCCDF 1.2 prefix which we will strip to avoid very long filenames
PROFILE_ID_PREFIX = ("^xccdf_org.*content_profile_")


def get_benchmark_id_title_map(input_tree):
    """
    Extracts a mapping of benchmark IDs to their titles from an XML tree.

    Args:
        input_tree (xml.etree.ElementTree.ElementTree): The XML tree containing benchmark data.

    Returns:
        dict: A dictionary where the keys are benchmark IDs (str) and the values are benchmark
              titles (str).
    """
    input_root = input_tree.getroot()
    ret = {}
    candidates = []
    scrape_benchmarks(input_root, XCCDF12_NS, candidates)

    for _, elem in candidates:
        _id = elem.get("id")
        if _id is None:
            continue

        title = "<unknown>"
        for element in elem.findall("{%s}title" % (XCCDF12_NS)):
            title = element.text
            break

        ret[_id] = title

    return ret


def get_profile_choices_for_input(input_tree, benchmark_id, tailoring_tree):
    """
    Returns a dictionary that maps profile_ids to their respective titles.

    Args:
        input_tree (ElementTree): The XML tree containing the benchmark profiles.
        benchmark_id (str): The ID of the benchmark to filter profiles.
        tailoring_tree (ElementTree, optional): An optional XML tree containing tailored profiles.

    Returns:
        dict: A dictionary where keys are profile IDs and values are profile titles.
    """
    # Ideally oscap would have a command line to do this, but as of now it
    # doesn't so we have to implement it ourselves. Importing openscap Python
    # bindings is nasty and overkill for this.

    ret = {}

    def scrape_profiles(root_element, namespace, dest):
        candidates = \
            list(root_element.findall(".//{%s}Benchmark" % (namespace)))
        if root_element.tag == "{%s}Benchmark" % (namespace):
            candidates.append(root_element)

        for benchmark in candidates:
            if benchmark.get("id") != benchmark_id:
                continue

            for elem in benchmark.findall(".//{%s}Profile" % (namespace)):
                id_ = elem.get("id")
                if id_ is None:
                    continue

                title = "<unknown>"
                for element in elem.findall("{%s}title" % (namespace)):
                    title = element.text
                    break

                dest[id_] = title

    input_root = input_tree.getroot()
    scrape_profiles(
        input_root, XCCDF12_NS, ret
    )

    if tailoring_tree is not None:
        tailoring_root = tailoring_tree.getroot()
        scrape_profiles(
            tailoring_root, XCCDF12_NS, ret
        )

    return ret


def get_profile_short_id(long_id):
    """
    Shortens the given profile ID if it matches the XCCDF 1.2 long ID format.

    Args:
        long_id (str): The long profile ID to be shortened.

    Returns:
        str: The shortened profile ID if the long ID matches the XCCDF 1.2 format, otherwise
             returns the original long ID.
    """
    if re.search(PROFILE_ID_PREFIX, long_id):
        return long_id[re.search(PROFILE_ID_PREFIX, long_id).end():]

    return long_id


def scrape_benchmarks(root, namespace, dest):
    """
    Add all benchmark elements in root to dest list.

    This function searches for all elements with the tag 'Benchmark' within the given XML root
    element, using the specified namespace. It then adds these elements to the destination list
    'dest' along with their namespace. If the root element itself is a 'Benchmark', it is also
    added to the list.

    Args:
        root (xml.etree.ElementTree.Element): The root XML element to search within.
        namespace (str): The XML namespace to use when searching for 'Benchmark' elements.
        dest (list): The list to which found 'Benchmark' elements and their namespace will be added.

    Returns:
        None
    """
    dest.extend([
        (namespace, elem)
        for elem in list(root.findall(".//{%s}Benchmark" % (namespace)))
    ])
    if root.tag == "{%s}Benchmark" % (namespace):
        dest.append((namespace, root))

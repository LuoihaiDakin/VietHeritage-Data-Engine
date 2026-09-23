import os
import json
import argparse


def get_project_root():
    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


def load_catalog(catalog_path):
    if not os.path.exists(catalog_path):
        print(f"ERROR: Catalog not found: {catalog_path}")
        return []

    try:
        with open(catalog_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        print("ERROR: Cannot read catalog.")
        print(error)
        return []


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def match_text(value, query):
    value = normalize_text(value)
    query = normalize_text(query)

    if not query:
        return True

    return query in value


def search_catalog(
    catalog,
    keyword=None,
    category=None,
    dynasty=None,
    period=None,
    motif=None,
    region=None,
    quality=None,
    vectorized=False,
    segmented=False,
    normalized=False,
    restored=False,
    preprocessed=False
):
    results = []

    for item in catalog:

        if keyword:
            searchable_text = " ".join([
                normalize_text(item.get("filename")),
                normalize_text(item.get("category")),
                normalize_text(item.get("period")),
                normalize_text(item.get("dynasty")),
                normalize_text(item.get("motif")),
                normalize_text(item.get("region")),
                normalize_text(item.get("source"))
            ])

            if normalize_text(keyword) not in searchable_text:
                continue

        if category:
            if not match_text(item.get("category"), category):
                continue

        if dynasty:
            if not match_text(item.get("dynasty"), dynasty):
                continue

        if period:
            if not match_text(item.get("period"), period):
                continue

        if motif:
            if not match_text(item.get("motif"), motif):
                continue

        if region:
            if not match_text(item.get("region"), region):
                continue

        if quality:
            item_quality = item.get("quality")

            if isinstance(item_quality, dict):
                item_classification = item_quality.get(
                    "quality",
                    ""
                )
            else:
                item_classification = ""

            if normalize_text(item_classification) != normalize_text(quality):
                continue

        processing = item.get("processing", {})

        if vectorized and not processing.get("vectorized", False):
            continue

        if segmented and not processing.get("segmented", False):
            continue

        if normalized and not processing.get("normalized", False):
            continue

        if restored and not processing.get("restored", False):
            continue

        if preprocessed and not processing.get("preprocessed", False):
            continue

        results.append(item)

    return results


def print_result(item, index):
    print("----------------------------------------")
    print(f"Result #{index}")
    print(f"ID:       {item.get('id', 'unknown')}")
    print(f"Filename: {item.get('filename', 'unknown')}")
    print(f"Path:     {item.get('path', 'unknown')}")
    print(f"Category: {item.get('category', 'unknown')}")
    print(f"Period:   {item.get('period', 'unknown')}")
    print(f"Dynasty:  {item.get('dynasty', 'unknown')}")
    print(f"Motif:    {item.get('motif', 'unknown')}")
    print(f"Region:   {item.get('region', 'unknown')}")

    quality = item.get("quality")

    if isinstance(quality, dict):
        print(
            f"Quality:  "
            f"{quality.get('quality', 'unknown')}"
        )

        print(
            f"Score:    "
            f"{quality.get('overall_score', 'unknown')}"
        )

    processing = item.get("processing", {})

    print(
        "Processing:"
        f" preprocess={processing.get('preprocessed', False)},"
        f" restore={processing.get('restored', False)},"
        f" normalize={processing.get('normalized', False)},"
        f" segment={processing.get('segmented', False)},"
        f" vector={processing.get('vectorized', False)}"
    )


def print_summary(results):
    print()
    print("========================================")
    print("             SEARCH SUMMARY")
    print("========================================")
    print(f"Results found: {len(results)}")
    print()


def save_results(results, output_path):
    output_directory = os.path.dirname(output_path)

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )


def build_argument_parser():

    parser = argparse.ArgumentParser(
        description="VietHeritage Data Engine Search Engine"
    )

    parser.add_argument(
        "--keyword",
        type=str,
        help="Search keyword"
    )

    parser.add_argument(
        "--category",
        type=str,
        help="Search by category"
    )

    parser.add_argument(
        "--dynasty",
        type=str,
        help="Search by dynasty"
    )

    parser.add_argument(
        "--period",
        type=str,
        help="Search by historical period"
    )

    parser.add_argument(
        "--motif",
        type=str,
        help="Search by motif"
    )

    parser.add_argument(
        "--region",
        type=str,
        help="Search by region"
    )

    parser.add_argument(
        "--quality",
        type=str,
        choices=[
            "GOOD",
            "ACCEPTABLE",
            "POOR"
        ],
        help="Search by quality classification"
    )

    parser.add_argument(
        "--vectorized",
        action="store_true",
        help="Only return vectorized assets"
    )

    parser.add_argument(
        "--segmented",
        action="store_true",
        help="Only return segmented assets"
    )

    parser.add_argument(
        "--normalized",
        action="store_true",
        help="Only return normalized assets"
    )

    parser.add_argument(
        "--restored",
        action="store_true",
        help="Only return restored assets"
    )

    parser.add_argument(
        "--preprocessed",
        action="store_true",
        help="Only return preprocessed assets"
    )

    parser.add_argument(
        "--save",
        type=str,
        help="Save search results to JSON file"
    )

    return parser


def main():

    project_root = get_project_root()

    catalog_path = os.path.join(
        project_root,
        "metadata",
        "heritage_catalog.json"
    )

    print("========================================")
    print("      VietHeritage Search Engine")
    print("========================================")
    print()

    catalog = load_catalog(catalog_path)

    if not catalog:
        print("ERROR: Catalog is empty.")
        print()
        print(
            "Run this first:"
        )
        print(
            "python metadata/build_catalog.py"
        )
        return

    parser = build_argument_parser()

    args = parser.parse_args()

    results = search_catalog(
        catalog=catalog,
        keyword=args.keyword,
        category=args.category,
        dynasty=args.dynasty,
        period=args.period,
        motif=args.motif,
        region=args.region,
        quality=args.quality,
        vectorized=args.vectorized,
        segmented=args.segmented,
        normalized=args.normalized,
        restored=args.restored,
        preprocessed=args.preprocessed
    )

    if not results:
        print("No results found.")
        return

    for index, item in enumerate(results, start=1):
        print_result(item, index)

    print_summary(results)

    if args.save:

        save_path = args.save

        if not os.path.isabs(save_path):
            save_path = os.path.join(
                project_root,
                save_path
            )

        save_results(
            results,
            save_path
        )

        print(
            f"Results saved to: {save_path}"
        )


if __name__ == "__main__":
    main()
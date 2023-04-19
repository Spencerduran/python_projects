import argparse
import json
import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


def get_docs(es_read, search_params: dict, es_read_index: str):
    """ query elasticsearch and store response documents """
    res = {}
    print("Querying elastic, results:")
    # Query elastic
    attempt = 0
    while attempt < 3:
        try:
            res = es_read.search(index=es_read_index, body=search_params)
            if res:
                break
        except Exception as e:
            print(e)
            attempt += 1
    # Parse, format and write response docs to output file
    hits = res["hits"]["hits"]
    docs = []
    for hit in hits:
        docs.append(hit["_source"])
        print(f'Source: {hit["_source"]}')
    return docs


def write_docs(es_write, docs: list, es_write_index: str):
    """ write documents to elasticsearch """
    print("Writing to elastic, responses:")
    attempt = 0
    for doc in docs:
        while attempt < 3:
            try:
                source_id = doc["data_source_id"]
                res = es_write.index(
                    index=es_write_index,
                    doc_type="_doc",
                    id=source_id,
                    body=doc,
                )
                print(f'\nSource: {res["_id"]} \nResult: {res["result"]}\nShards: {res["_shards"]}')
                break
            except Exception as e:
                print(e)
                attempt += 1


def main():
    """Query and optionally write to specified elasticsearch environments
    Args:
        -read <compliance/production/sandbox/staging>
        -write <compliance/production/sandbox/staging> (optional)
    """
    load_dotenv()
    ca_cert_path = os.getenv("CERT_PATH")
    # Build es client
    read_creds = json.loads(os.getenv(args.read.upper()))
    es_read_index = os.getenv("ES_READ_INDEX")
    es_read = Elasticsearch(
        [read_creds["URL"]],
        http_auth=(read_creds["USER"], read_creds["PASS"]),
        use_ssl=True,
        ca_certs=ca_cert_path,
    )
    search_params = json.loads(os.getenv("QUERY"))
    docs = get_docs(es_read, search_params, es_read_index)
    if args.write:
        write_creds = json.loads(os.getenv(args.write.upper()))
        es_write_index = os.getenv("ES_WRITE_INDEX")
        es_write = Elasticsearch(
            [write_creds["URL"]],
            http_auth=(write_creds["USER"], write_creds["PASS"]),
            use_ssl=True,
            ca_certs=ca_cert_path,
        )

        write_docs(es_write, docs, es_write_index)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-read", action="store", type=str)
    parser.add_argument("-write", action="store", type=str)
    args = parser.parse_args()
    main()

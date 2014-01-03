#!/usr/bin/env python2
__author__ = 'escherba'

import argparse
import sys
import json
import calendar
import dateutil.parser as dateutil_parser
from collections import Counter
from functools import partial
from itertools import imap, chain, islice
from math import log
from lsh import Cluster, WordShingler
from test.utils import sort_by_length, JsonRepr, smart_open


class Options(JsonRepr):
    """Command-line option globals
    """
    file_path = None
    output_path = None
    bands = 3
    bandwidth = 3
    shingle_size = 3
    quiet = False
    no_user_id = False
    min_cluster = 6
    head = None
    #timestamp = False
    #alias = False


def mac_get_post_id(json_obj, n):
    return json_obj[u'object'][u'post_id'] + '.' + str(n)


def get_shingles(shingler, obj, options):
    content = obj[u'content']
    shingles = shingler.get_shingles(content)

    # optionally add user_id as a shingle
    if not options.no_user_id:
        shingles.add((obj[u'user_id'],))

    '''
    if options.timestamp:
        shingles.add((obj[u'timestamp'],))

    if options.alias and u'alias' in obj:
        shingles.add((obj[u'alias'],))
    '''
    return shingles


def mac_gather_stats(clusters, options=None):
    """

    :throws ZeroDivisionError:
    :returns: Theil uncertainty index (a homogeneity measure)
    :rtype: dict
    """
    def entropy(N, n):
        """

        :param N: sample count
        :param n: number of bits
        :return: (Information) entropy
        :rtype: float
        """
        n_ = float(n)
        if n_ > 0.0:
            ratio = n_ / float(N)
            return - ratio * log(ratio)
        else:
            return 0.0

    def average(l):
        """Find average
        :param l: a list of numbers
        :type l: list
        :returns: average
        :rtype: float
        """
        xs = list(l)
        return float(reduce(lambda x, y: x + y, xs)) / float(len(xs))

    def sumsq(l):
        """Sum of squares
        :param l: a list of numbers
        :type l: list
        :returns: sum of squares
        :rtype: float
        """
        xs = list(l)
        avg = average(xs)
        return sum((el - avg) ** 2 for el in xs)

    def explained_var(l):
        """Explained variance
        :param l: a list of list
        :type l: list
        :returns: explained variance
        :rtype: float
        """
        residual_var = sum(imap(sumsq, l))
        total_var = sumsq(chain.from_iterable(l))
        return 1.0 - residual_var / total_var

    result = {}

    post_count = 0
    numerator = 0.0
    multiverse = Counter()
    all_times = []
    cluster_count = 0
    tag_counter = Counter()
    shingler = WordShingler(options.shingle_size)

    for cluster_id, cluster in enumerate(islice(clusters, 0, options.head)):
        universe = Counter()
        times = []
        posts = cluster[u'posts']
        cluster_size = len(posts)
        if cluster_size >= options.min_cluster:
            cluster_count += 1
            for post_id, json_obj in posts.iteritems():
                try:
                    tags = json_obj[u'impermium'][1][u'4.0'][u'tags']
                except KeyError:
                    tags = []
                except TypeError:
                    tags = []
                for tag in tags:
                    tag_counter[tag] += 1
                obj = json_obj[u'object']
                timestamp = obj[u'timestamp']
                t = dateutil_parser.parse(timestamp)
                times.append(calendar.timegm(t.utctimetuple()))
                shingles = get_shingles(shingler, obj, options)
                universe.update(shingles)

            post_count += cluster_size
            all_times.append(times)
            numerator += sum(imap(partial(entropy, cluster_size),
                                  universe.values()))
            multiverse.update(universe)

    # Calculate uncertainty index
    uncertainty_index = None
    try:
        denominator = float(cluster_count) * \
            sum(imap(partial(entropy, post_count), multiverse.values()))
        uncertainty_index = 1.0 - numerator / denominator
    except ZeroDivisionError:
        pass
    finally:
        result['uncertainty_index'] = uncertainty_index

    # Calculate variance ratio
    time_coeff = None
    try:
        time_coeff = explained_var(all_times)
    except ZeroDivisionError:
        pass
    except TypeError:
        pass
    finally:
        result['time_coeff'] = time_coeff

    # Set the rest of the variables
    result['num_clusters'] = cluster_count
    result['num_comments_in_clusters'] = post_count
    result['num_tags'] = tag_counter
    return result


def cluster_from_mac_log(options):
    def output_clusters(unfiltered_sets, data):
        with smart_open(options.output_path) as fh:
            for cluster_id, cluster in enumerate(sort_by_length(unfiltered_sets)):
                posts = {}
                for post_id in cluster:
                    if post_id in posts:
                        # guarantee that post_id occurs only once
                        raise KeyError
                    else:
                        posts[post_id] = data[post_id]
                d = {
                    "cluster_id": cluster_id,
                    "length": len(cluster),
                    "posts": posts
                }
                print >>fh, json.dumps(d)
                yield d

    cluster_builder = Cluster(bands=options.bands,
                              bandwidth=options.bandwidth)
    shingler = WordShingler(options.shingle_size)

    data = {}
    with open(options.file_path) as mac_log:
        for line_num, line in enumerate(islice(mac_log, 0, options.head)):
            if (not options.quiet) and (not line_num % 10000):
                sys.stderr.write("Processing line " + str(line_num) + "\n")
            json_obj = json.loads(line)
            post_id = mac_get_post_id(json_obj, line_num)
            cluster_builder.add_set(get_shingles(shingler, json_obj[u'object'], options), post_id)
            data[post_id] = json_obj

    clusters = cluster_builder.get_clusters()
    stats = mac_gather_stats(output_clusters(clusters, data),
                             options=options)
    sys.stderr.write(json.dumps(
        {"options": options.as_dict(),
         "stats": stats}) + "\n")


def process_mac_log(args):
    """Process a MAC log"""
    options = Options()
    options.assign(args)
    cluster_from_mac_log(options)


def summarize_file(args):
    """Summarize an intermediate"""
    def read_intermediate(file_path):
        with open(file_path) as mac_log:
            for line in mac_log:
                yield json.loads(line)

    options = Options()
    options.assign(args)
    stats = mac_gather_stats(read_intermediate(options.file_path),
                             options=options)
    sys.stderr.write(json.dumps(
        {"options": options.as_dict(),
         "stats": stats}) + "\n")


if __name__ == '__main__':
    """
    A sample bash-script illustrating how to run this

    python process_MAC_log.py \
        --shingle_size 4 \
        --quiet \
        --file data/detail.log.1 > /dev/null
    """
    parser = argparse.ArgumentParser(description='Perform clustering.')

    # add common arguments up here
    parser.add_argument('--quiet', action='store_true',
                        help='whether to be quiet', required=False)
    parser.add_argument('--min_cluster', type=int, dest='min_cluster', default=4,
                        help='minimum cluster size for quality evaluation', required=False)
    parser.add_argument('--head', type=int, dest='head', default=None,
                        help='how many lines from file to process (all if not set)', required=False)
    parser.add_argument('--file', type=str, dest='file_path', required=True,
                        help='Path to log file to process (required)')

    # for specialized functionality, use subparsers
    subparsers = parser.add_subparsers()

    # subparser: cluster
    parser_cluster = subparsers.add_parser('cluster', help='cluster a MAC log file and produce an intermediate')
    parser_cluster.add_argument('--shingle_size', type=int, dest='shingle_size', default=4,
                                help='shingle length (in tokens)', required=False)
    parser_cluster.add_argument('--bands', type=int, dest='bands', default=4,
                                help='number of bands', required=False)
    parser_cluster.add_argument('--bandwidth', type=int, dest='bandwidth', default=3,
                                help='rows per band', required=False)
    parser_cluster.add_argument('--no_user_id', action='store_true',
                                help='exclude user_id field', required=False)
    parser_cluster.add_argument('--output', type=str, dest='output_path', required=False,
                                help='Path to output')
    parser_cluster.set_defaults(func=process_mac_log)

    # subparser: summarize
    parser_summarize = subparsers.add_parser('summarize', help='summarize an intermediate')
    parser_summarize.set_defaults(func=summarize_file)

    # standard arg processing...
    args = parser.parse_args()
    args.func(args)

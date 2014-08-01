#!/usr/bin/env python2

import os
import sys
import yaml
from pymaptools import UnionFind
from mrjob import protocol as mr_protocol
from mrjob.job import MRJob
from mrjob.step import MRStep
from operator import itemgetter
from collections import Counter
from lsh_hdc.cluster import HDClustering
from content_rules import ContentFilter

fn = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/mac.yaml'))
sys.stderr.write("--> " + fn + "\n")
with open(fn, 'r') as fh:
    mac_cfg = yaml.load(fh)


hdc = HDClustering(cfg=mac_cfg['model'],
                   content_filter=ContentFilter(),
                   get_body=itemgetter('content'),
                   get_label=itemgetter('post_id'),
                   get_prefix=itemgetter('user_id'))


class MRCluster(MRJob):

    INPUT_PROTOCOL = mr_protocol.JSONValueProtocol
    INTERNAL_PROTOCOL = mr_protocol.JSONProtocol
    OUTPUT_PROTOCOL = mr_protocol.JSONProtocol

    def lsh_mapper(self, _, data):
        obj = data['object']
        for pair in hdc.mapper(obj):
            yield pair

    def lsh_combiner(self, key, vals):
        ckey, cvals = hdc.reducer(key, vals)
        for cval in cvals:
            yield ckey, cval

    def lsh_reducer(self, key, vals):
        rkey, rvals = hdc.reducer(key, vals)

        # filter out all groupings of size one or smaller
        if len(rvals) > 1:
            yield rkey, rvals

    def ab_mapper(self, lsh, data):
        sorted_data = sorted(data)  # sort on labels
        key = sorted_data[0]
        # key is label + sketch pair
        yield key, (lsh, sorted_data[1:])

    def uniq_reducer(self, key, vals):
        uniq = set()
        for lsh, tuples in vals:
            uniq.add(tuple(tuple(t) for t in tuples))
        for val in uniq:
            yield key, val

    def cluster_reducer(self, key, vals):

        sketch_dist = hdc.sketch_dist_fn
        max_dist = hdc.max_dist
        min_support = hdc.min_support

        label, sketch = key
        unclustered_counter = Counter()
        unclustered_sketches = dict()
        clustered_sketches = {label: sketch}
        unclustered = []
        for val in vals:
            lsh, tuples = val
            if lsh is None:
                clustered_sketches.update(tuples)
            else:
                unclustered_counter.update(t[0] for t in tuples)
                unclustered_sketches.update(tuples)
                unclustered.append(val)

        # from unclustered labels, obtain new labels to cluster
        is_close = lambda t: \
            unclustered_counter[t[0]] >= min_support and \
            sketch_dist(sketch, t[1]) <= max_dist
        filtered_labels = set(t[0] for t in unclustered_sketches.iteritems()
                              if is_close(t))

        # merge new labels with already linked clusters
        clustered_sketches.update((lbl, unclustered_sketches[lbl])
                                  for lbl in filtered_labels)
        clustered_labels = set(clustered_sketches.keys())

        # emit ("c", [remaining tuples]) for each tuple in clustered
        if len(clustered_labels) > 1:
            for lbl in clustered_labels:
                new_key = (lbl, clustered_sketches[lbl])
                val = [(x, clustered_sketches[x]) for x in clustered_labels
                       if x != lbl]
                yield new_key, (None, val)

        # remove all the clustered labels from the unclustered groups and
        # emit unclustered groups on a rotated key
        for lsh, tuples in unclustered:
            remaining = filter(lambda t: t[0] not in clustered_labels, tuples)
            if len(remaining) > 1:
                yield remaining[0], (lsh, remaining[1:])

    def union_mapper(self, key, val):
        """ emit only 'good' clusters """
        lsh, tuples = val
        if lsh is None:
            tuples.append(key)
            yield None, tuples

    def union_reducer(self, key, vals):
        """ find connected components """
        uf = UnionFind()
        for tuples in vals:
            uf.union(*[t[0] for t in tuples])
        for i, s in enumerate(uf.sets()):
            yield i, s

    def steps(self):
        return [
            MRStep(mapper=self.lsh_mapper,
                   combiner=self.lsh_combiner,
                   reducer=self.lsh_reducer),
            MRStep(mapper=self.ab_mapper,
                   reducer=self.cluster_reducer),
            MRStep(reducer=self.cluster_reducer),
            MRStep(mapper=self.union_mapper,
                   reducer=self.union_reducer)
        ]


if __name__ == '__main__':
    MRCluster.run()

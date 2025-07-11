# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 23:42:17 2022

@author: steph
"""

import sys
from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('first Spark app').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 8) # make sure we have Python 3.8+
assert spark.version >= '3.2' # make sure we have Spark 3.2+


schema = types.StructType([
    types.StructField('id', types.IntegerType()),
    types.StructField('x', types.FloatType()),
    types.StructField('y', types.FloatType()),
    types.StructField('z', types.FloatType()),
])


def main(in_directory, out_directory):
    # Read the data from the JSON files
    xyz = spark.read.json(in_directory, schema=schema)
    #xyz.show(); return

    # Create a DF with what we need: x, (soon y,) and id%10 which we'll aggregate by.
    with_bins = xyz.select(
        xyz['x'],
        xyz['y'],
        # TODO: also the y values
        (xyz['id'] % 10).alias('bin'),
    )
    #with_bins.show(); return

    # Aggregate by the bin number.
    grouped = with_bins.groupBy(with_bins['bin'])
    col = with_bins['y']
    groups = grouped.agg(
        functions.sum(with_bins['x']),
        functions.avg(col),
        # TODO: output the average y value. Hint: avg
        functions.count('*'))

    # We know groups has <=10 rows, so it can safely be moved into two partitions.
    groups = groups.sort(groups['bin']).coalesce(2)
    groups.write.csv(out_directory, compression=None, mode='overwrite')


if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)

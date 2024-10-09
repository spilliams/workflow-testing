#!/usr/bin/env python3
# from os import environ
import json
import sys

print(f"{len(sys.argv)} arg(s)")
print(f"{sys.argv}")
injson = json.loads(sys.argv[1])
# extradims = json.loads(sys.argv[2])
# print(json.dumps(extradims))
# first arg should be json that describes the metric:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/put_metric_data.html
data = injson['MetricData'][0]
print(f'namespace:{injson['Namespace']}')

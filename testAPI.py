import boto3
import time

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
streams = boto3.client("dynamodbstreams", region_name="ap-southeast-1")
table = dynamodb.Table("jobs")

stream_arn = table.latest_stream_arn
print("Stream ARN:", stream_arn)

shards = streams.describe_stream(StreamArn=stream_arn)["StreamDescription"]["Shards"]
print(f"Shards found: {len(shards)}")

# Init iterators
iterators = {}
for shard in shards:
    shard_id = shard["ShardId"]
    resp = streams.get_shard_iterator(
        StreamArn=stream_arn,
        ShardId=shard_id,
        ShardIteratorType="LATEST",
    )
    iterators[shard_id] = resp["ShardIterator"]

print("Iterators ready — now insert something into the table, then wait...")
time.sleep(10)

# Check for records
for shard_id, iterator in iterators.items():
    resp = streams.get_records(ShardIterator=iterator)
    records = resp.get("Records", [])
    print(f"Shard {shard_id}: {len(records)} record(s)")
    for r in records:
        print(" ->", r["eventName"], r["dynamodb"].get("NewImage"))
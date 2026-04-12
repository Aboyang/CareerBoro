import boto3
from decimal import Decimal
from typing import List, Dict, Any, Optional


def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


class JobDB:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")
        self.table = self.dynamodb.Table("jobs")
        self.streams_client = boto3.client("dynamodbstreams", region_name="ap-southeast-1")
        self._shard_iterators: Dict[str, Optional[str]] = {}  # persisted iterators

    def get_jobs(self) -> List[Dict[str, Any]]:
        response = self.table.scan()
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self.table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
        return decimal_to_native(items)

    def _init_shard_iterators(self, stream_arn: str):
        """Initialize LATEST iterators for all shards (called once on first poll)."""
        shards = self.streams_client.describe_stream(
            StreamArn=stream_arn
        )["StreamDescription"]["Shards"]

        for shard in shards:
            shard_id = shard["ShardId"]
            if shard_id not in self._shard_iterators:
                resp = self.streams_client.get_shard_iterator(
                    StreamArn=stream_arn,
                    ShardId=shard_id,
                    ShardIteratorType="LATEST",  # only new records from this point
                )
                self._shard_iterators[shard_id] = resp["ShardIterator"]

    def has_new_stream_records(self) -> bool:
        try:
            stream_arn = self.table.latest_stream_arn
            if not stream_arn:
                return False

            # Set up iterators on first call
            if not self._shard_iterators:
                self._init_shard_iterators(stream_arn)
                return False  # skip this round, just initializing

            found_new = False

            for shard_id, iterator in list(self._shard_iterators.items()):
                if not iterator:
                    continue

                resp = self.streams_client.get_records(ShardIterator=iterator)
                records = resp.get("Records", [])

                # Always update to the next iterator to advance the cursor
                self._shard_iterators[shard_id] = resp.get("NextShardIterator")

                if records:
                    print(f"[Stream] {len(records)} new record(s) on shard {shard_id}")
                    found_new = True

            return found_new

        except Exception as e:
            print(f"[JobDB] Stream check error: {e}")
            return False
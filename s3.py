import boto3


def list_buckets():
    # session = boto3.Session(profile_name="mle-intern-dev")
    s3 = boto3.client('s3')

    existing_buckets = []
    for bucket in s3.list_buckets()["Buckets"]:
        existing_buckets.append(bucket["Name"])

    return existing_buckets


def created_folder(bucket, prefix):
    s3 = boto3.resource("s3")
    my_bucket = s3.Bucket(bucket)

    var = []

    for object_summary in my_bucket.objects.filter(Prefix=prefix):
        var.append(object_summary.key)
    return var

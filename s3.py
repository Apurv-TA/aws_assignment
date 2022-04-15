import boto3


def list_buckets():
    session = boto3.Session(profile_name="mle-intern-dev")
    s3 = session.client('s3')

    existing_buckets = []
    for bucket in s3.list_buckets()["Buckets"]:
        existing_buckets.append(bucket["Name"])

    return existing_buckets


def created_folder():
    session = boto3.Session(profile_name="mle-intern-dev")
    s3 = session.resource("s3")
    my_bucket = s3.Bucket("tiger-mle-pg")

    var = []

    for object_summary in my_bucket.objects.filter(Prefix="home/apurv.master@tigeranalytics.com"):
        var.append(object_summary.key)
    return var


# if __name__ == "__main__":
#     print(list_buckets())
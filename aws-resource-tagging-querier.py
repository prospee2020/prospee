import boto3
import argparse

def input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True, help="SQL query to filter tagged resources output")
    parser.add_argument("--key", required=True, help="SQL query to filter tagged resources output")
    parser.add_argument("--query", default="select * from s3object", help="SQL query to filter tagged resources output")
    return parser.parse_args()

    def main():
    args = input_args()
    s3 = boto3.client('s3')
    response = s3.select_object_content(
        Bucket=args.bucket,
        Key=args.key,
        ExpressionType='SQL',
        Expression=args.query,
        InputSerialization = {'CSV': {"FileHeaderInfo": "Use"}},
        OutputSerialization = {'CSV': {}},
    )

    for event in response['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            print(records)

if __name__ == '__main__':
    main()


    ######### aws s3 cp /tmp/qa-tagged-resources.csv s3://[REPLACE-WITH-YOUR-S3-BUCKET] #########



    #####The query ######
    ########export AWS_PROFILE= CENTRAL_AWS_ACCOUNT
####python aws-tagged-resources-querier \
#     --bucket [REPLACE-WITH-YOUR-S3-BUCKET] \
#     --key qa-tagged-resources.csv \
#     --query "select ResourceArn from s3object s \
#              where s.ResourceArn like 'arn:aws:ec2%route-table%' \
#                and s.TagKey='aws:cloudformation:stack-name'"  ########



#####  main url https://aws.amazon.com/blogs/architecture/how-to-efficiently-extract-and-query-tagged-resources-using-the-aws-resource-tagging-api-and-s3-select-sql/  ######

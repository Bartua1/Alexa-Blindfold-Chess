import boto3
import os

def create_table():
    # Use environment variable or default to us-east-1
    region = os.environ.get("AWS_REGION", "us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table_name = 'BlindfoldChessData'
    
    print(f"Attempting to create DynamoDB table '{table_name}' in region '{region}'...")
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',  # Standard partition key for ASK DynamoDB adapter
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Waiting for table to be created...")
        table.wait_until_exists()
        print(f"Table '{table_name}' created successfully!")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table '{table_name}' already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")
        print("\nMake sure you have AWS credentials configured.")
        print("You can run 'aws configure' if you have the AWS CLI installed,")
        print("or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")

if __name__ == '__main__':
    create_table()

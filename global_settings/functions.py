import boto3
import datetime
from botocore.exceptions import NoCredentialsError, ClientError
from .models import CloudfrontDistribution

def invalidate_cloudfront_caches():
    try:
        distribution = CloudfrontDistribution.objects.all()[0]
        client = boto3.client('cloudfront')
        response = client.create_invalidation(
            DistributionId=distribution.distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [
                        '/apps/cms/api/*' # invalidate the entire cache for the website
                    ],
                },
                'CallerReference': str(datetime.datetime.now().strftime('%m%d%Y%H%M'))
            }
        )
    except CloudfrontDistribution.DoesNotExist:
        return
    except IndexError:
        return
    except NoCredentialsError:
        print('No AWS credentials set - unable to invalidate cache')
    except ClientError as e:
            print("Unexpected AWS error: %s" % e)
from aws_cdk import (
    NestedStack,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    CfnParameter
)
from constructs import Construct
import configparser
config = configparser.ConfigParser()
config.read("config.ini")

class NotificationStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SNS Topic
        topic = sns.Topic(
            self, 
            "ClaimProcessTopic",
            topic_name="insuranceclaimClaimProcessNotification",
            display_name="Insurance Claim Notifications"
        )

        # Get email addresses from config
        try:
            email_addresses = config['NOTIFICATION']['complete_notification_reciepients'].split(',')
            # Strip whitespace from each email
            email_addresses = [email.strip() for email in email_addresses]
            
            # Add subscriptions for each email
            for email in email_addresses:
                if email:  # Only add if email is not empty
                    topic.add_subscription(
                        subscriptions.EmailSubscription(email)
                    )
        except KeyError as e:
            print(f"Error reading config: {e}")

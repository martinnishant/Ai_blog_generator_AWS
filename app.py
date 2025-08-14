import boto3
import botocore.config
import json
from datetime import datetime 

def blog_generate_using_bedrock(blogtopic:str)-> str:
    prompt = f"""<s>[INST]Human: Generate a blog post about {blogtopic}
    Assistant:[/INST]"""

    body = { 
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.7,
        "top_p": 0.9
    }



    try:
        bedrock = boto3.client("bedrock-runtime", region_name = "ap-south-1",
                               config = botocore.config.Config(read_timeout=150, retries = {'max_attempts':3}))

        response = bedrock.invoke_model(body=json.dumps(body), modelId = "meta.llama3-70b-instruct-v1:0")

        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    except Exception as e: 
        print(f"Error generating blog post: {e}")
        return "An error occurred while generating the blog post."
    
def save_blog_details_s3(s3_key, s3_bucket):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print(f"Blog post saved to S3 bucket")
         
    except Exception as e:
        print(f"Error saving blog post to S3: {e}")

def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']

    generate_blog = blog_generate_using_bedrock(blogtopic=blogtopic)
    

    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog_posts/{current_time}.txt"
        s3_bucket = "aws_bucket_blog"  
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)
    else:
        print("No blog was generated")

    return{
        'statusCode' :200,
        'body': json.dumps({
            'message': 'Blog post generated successfully',
            'blog_content': generate_blog
        })
    } 
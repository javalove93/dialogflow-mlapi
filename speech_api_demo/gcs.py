import tempfile
from google.cloud import storage
from urlparse import urlparse

def download_gcs(gcs_url, out_file):
    client = storage.Client()
    o = urlparse(gcs_url)
    
    bucket = o.netloc
    filename = o.path

    bucket = client.get_bucket(bucket)
    blob = bucket.get_blob(filename[1:])
    blob.download_to_file(out_file)

def upload_gcs(gcs_url, in_file_name):
    client = storage.Client()
    o = urlparse(gcs_url)
    
    bucket = o.netloc
    filename = o.path

    # Set a expiration(life cycle) date
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(filename[1:])
    blob.upload_from_filename(filename=in_file_name)

def delete_gcs(gcs_url):
    client = storage.Client()
    o = urlparse(gcs_url)
    
    bucket = o.netloc
    filename = o.path

    bucket = client.get_bucket(bucket)
    blob = bucket.blob(filename[1:])
    blob.delete()



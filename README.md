# Dropit Server

This server acts as the intermediary and record keeper for S3 backed uploads from the dropit client.

Basically, you get an account on this machine, and then the API signs upload requests for the client.

This is "better" than putting keys directly in the client for three reasons.

  1. Rate/size limiting is now an option
  1. Direct accountability for uploads is tied to a username/password
  1. You can have pretty preview pages for uploads

# Running It

You will need Python ~2.7 and redis.

Everyone has their own favorite setup, but I like gunicorn + gevent behind nginx.

It works fine on Heroku.

## Configuration

By default, we load up a configuration file whose path is specified by the environment variable `CONFIG_PATH`.

In this config we need the following keys:

  * AWS_ACCESS_KEY
  * AWS_SECRET_KEY
  * S3_BUCKET
  * UPLOAD_URL_BASE
  
If you can't figure out what the first three are, you should go do some reading on S3.

`UPLOAD_URL_BASE` is the root of where direct uploads go.  This is so if you CNAME your S3 bucket you can specify that.
In general this should be something like `http://mybucket.s3.amazonaws.com/` but could be anything as long as it's all
configured correctly.

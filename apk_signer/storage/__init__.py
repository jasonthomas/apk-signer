import tempfile

from django.conf import settings

from boto.s3.connection import S3Connection


def connect(**kw):
    # TODO: pool connections?
    return S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY,
                        **kw)


def bucket(conn=None):
    if not conn:
        conn = connect()
    return conn.get_bucket(settings.S3_BUCKET)


def get_apk(key_path, conn=None, suffix='.apk'):
    if not conn:
        conn = connect()

    bkt = bucket(conn=conn)
    key = bkt.get_key(key_path)
    if not key:
        # TODO: maybe add a retry loop here if we hit this error a lot.
        raise NoSuchKey('Key {path} does not exist in {bkt}'
                        .format(path=key_path, bkt=bkt))
    fp = tempfile.NamedTemporaryFile(suffix=suffix)
    key.get_contents_to_file(fp)

    return fp


def put_signed_apk(fp, key_path, conn=None):
    if not conn:
        conn = connect()

    bkt = bucket(conn=conn)
    key = bkt.new_key(key_path)
    key.set_contents_from_file(fp)
    key.set_acl('public-read')


def get_app_key(key_path, conn=None):
    return get_apk(key_path, conn, '.p12')


def put_app_key(fp, key_path, conn=None):
    """ Look ma!  Duplication of logic!"""
    if not conn:
        conn = connect()

    bkt = bucket(conn=conn)
    if bkt.get_key(key_path) is not None:
        raise AppKeyAlreadyExists('App signing key {path} already exists in '
                                  '{bkt}'.format(path=key_path, bkt=bkt))
    key = bkt.new_key(key_path)
    key.set_contents_from_file(fp)
    key.set_acl('private')


class NoSuchKey(Exception):
    """The S3 key path does not exist"""


class AppKeyAlreadyExists(Exception):
    """An S3 entry already exists for that app key path"""

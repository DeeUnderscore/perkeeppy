import json
import random
import datetime

from camlistore.blobclient import Blob
from camlistore.exceptions import SigningError

CAMLI_VERSION = 1 # Schema version, per Perkeep

class SchemaObject(object):
    """
    A JSON object recognized by Perkeep

    While at the lower level, Perkeep blobs are just raw data, Perkeep
    understands some blobs which contain JSON data. This class allows a
    higher-level access to these objects. It wraps a :class:`Blob` object
    """

    def __init__(self, camli_type, data=None, needs_signing=False):
        self.data = { 'camliVersion': CAMLI_VERSION,
                      'camliType': camli_type } 

        if data:
            self.data.update(data)

        self.needs_signing = needs_signing

    def to_blob(self, signer=None):
        """ 
        Return a blob with object's JSON data.

        If :attr:`needs_signing` is set, a :class:`Signer` should be passed as
        ``signer``. If sigining is required, and this function is unable to sign
        the JSON, it will raise a :class:`SigningError`
        """

        #TODO: Keep a Blob in this object, and invalidate it when needed, so
        # that we can return Blobs from other things.

        if not self.needs_signing:
            # Perkeep generally uses tabs for indentation for stored blobs. This
            # should not matter, and our serialization is likely different, but 
            # we use tabs for consistency anyway
            return Blob(json.dumps(self.data, indent='\t').encode('utf8'))

        if not signer:
            raise SigningErorr('A signer was needed, and none was passed to to_blob()')

        return Blob(signer.sign_dict(self.data))


def get_permanode():
    """
    Get a new permanode, as a :class:`SchemaObject`. The permanode can then be
    made into a blob with :meth:`SchemaObject.to_blob()` and uploaded to server. 
    """

    rand_string = str(random.randrange(0, 1e20))

    return SchemaObject('permanode', 
                        data={'random': rand_string},
                        needs_signing=True)

def make_claim(pnode_id, key, action, value=None, date=None):
    """
    Make a claim for a permanode.

    ``pnode_id`` is the blobref of the permanode for which the claim will be
    made. This will not be checked – if it is invalid, the claim will submit 
    fine, but Perkeep will not use it for anything.

    ``key`` is the name of the attribute to set. ``action`` can be ``add``, to 
    add a new attribute value (from the ``value`` argument), ``set`` to replace 
    an old value with a new one in a single-value attribute, or ``del`` to 
    delete either a particular value of an attribute, or all values if ``value``
    is not set.

    ``date`` can be set to specify the date on the claim. If left ``None``,
    current time and date will be used. It can be either a class:`datetime`
    object, or a string. Strings will not be checked for validity. Naive
    datetime objects will be assumed to be UTC.

    This function returns a :class:`SchemaObject` which can then be made into a
    blob with :meth:`SchemaObject.to_blob()` for uploading.
    """

    #TODO: Maybe see about handling ClaimMeta objects?

    if action not in ('add', 'set', 'del'):
        raise ValueError('action must be "add", "set", or "del"')

    action = action + '-attribute'

    if date is None:
        # We want a tz-aware datetime, so that the isoformat output contains
        # timezone information
        date_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    elif isinstance(date, datetime.datetime):
        if date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None:
            date_str = date.astimezone(tz=datetime.timezone.utc).isoformat()
        
        else:
            # we assume naive datetimes are UTC
            date_str = date.replace(tzinfo=datetime.timezone.utc).isoformat()
        
    elif isinstance(date, str):
        date_str = date

    else:
        raise ValueError('date was supplied in a format that was not understood')
        

    data = { 'permaNode': pnode_id,
             'claimDate': date_str,
             'attribute': key,
             'claimType': action }
    
    if value:
        data['value'] = value

    return SchemaObject('claim', data=data, needs_signing=True)

    







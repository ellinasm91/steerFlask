from FlaskWebProject.uploaders.upload_helpers import get_dev_headers

import crud_safety
import io_transformers
from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.uploaders import upload_dummy


@app.route('/dummy/<collection_id>', methods=['GET'])
def dummy_create(collection_id=None):
    return upload_dummy.dummy_create(collection_id)


@app.route('/<collection_id>', methods=['GET'])
@app.route('/dev/<collection_id>/<mode>', methods=['GET'])
def read_bypass(collection_id, mode=DEBUG):
    out_data = crud_safety.read_bypass(collection_id, mode)
    return io_transformers.transform_output(out_data, {})


@app.route('/del/ru', methods=['GET'])
def delete_retailer_users():
    out_data = crud_safety.delete(RETAILER_USERS, get_dev_headers(), [])
    return io_transformers.transform_output(out_data, {})

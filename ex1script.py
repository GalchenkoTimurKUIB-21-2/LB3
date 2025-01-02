from bottle import route, request, response, run, abort
import json
from functools import wraps

# Basic Authentication
users = {"admin": "admin"}  # User credentials

def check_auth(username, password):
    return users.get(username) == password

def authenticate():
    response.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
    response.status = 401
    return {"error": "Unauthorized access"}

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.auth
        if not auth or not check_auth(auth[0], auth[1]):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Data Storage
catalog = {}  # In-memory dictionary for storing items

@route('/items', method=['GET', 'POST'])
@requires_auth
def items():
    if request.method == 'GET':
        return {"catalog": list(catalog.values())}

    elif request.method == 'POST':
        try:
            item = request.json
            if not item or 'id' not in item or 'name' not in item or 'price' not in item:
                abort(400, "Invalid item format. Must include 'id', 'name', and 'price'.")

            item_id = str(item['id'])
            if item_id in catalog:
                abort(400, f"Item with id {item_id} already exists.")

            catalog[item_id] = item
            response.status = 201
            return {"message": "Item added successfully", "item": item}

        except Exception as e:
            abort(500, str(e))

@route('/items/<id>', method=['GET', 'PUT', 'DELETE'])
@requires_auth
def item_detail(id):
    item_id = str(id)

    if request.method == 'GET':
        if item_id not in catalog:
            abort(404, f"Item with id {item_id} not found.")
        return catalog[item_id]

    elif request.method == 'PUT':
        try:
            updated_item = request.json
            if not updated_item or 'name' not in updated_item or 'price' not in updated_item:
                abort(400, "Invalid item format. Must include 'name' and 'price'.")

            if item_id not in catalog:
                abort(404, f"Item with id {item_id} not found.")

            catalog[item_id].update(updated_item)
            return {"message": "Item updated successfully", "item": catalog[item_id]}

        except Exception as e:
            abort(500, str(e))

    elif request.method == 'DELETE':
        if item_id not in catalog:
            abort(404, f"Item with id {item_id} not found.")

        deleted_item = catalog.pop(item_id)
        return {"message": "Item deleted successfully", "item": deleted_item}

if __name__ == "__main__":
    run(host='localhost', port=8000)

    """
    Запити 
    http://localhost:8000/items
    http://localhost:8000/items/<id>
    """
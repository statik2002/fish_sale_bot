from pprint import pprint

import requests
from environs import Env


env = Env()
env.read_env()

client_id = env('ELASTIC_PATH_CLIENT_ID')


def get_access_token(client_id):
    data = {
        'client_id': client_id,
        'grant_type': 'implicit',

    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()

    access_token = response.json().get('access_token')
    return access_token


def get_all_products(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    response = requests.get('https://api.moltin.com/catalog/products', headers=headers)
    response.raise_for_status()

    return response.json()


def get_product(token, product_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    data = {
        'include': 'component_products',
    }

    response = requests.get(f'https://api.moltin.com/catalog/products/{product_id}', headers=headers, params=data)
    response.raise_for_status()

    return response.json()


def get_product_pcm(token, product):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    data = {
        'include': 'component_products'
    }

    response = requests.get(f'https://api.moltin.com/pcm/products/{product}', headers=headers)
    response.raise_for_status()

    return response.json()


def get_cart(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    response = requests.get('https://api.moltin.com/v2/carts/:reference', headers=headers)
    response.raise_for_status()

    return response.json()


def add_product_to_cart(token, product_data):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    response = requests.post('https://api.moltin.com/v2/carts/:reference/items', headers=headers, json=product_data)
    response.raise_for_status()

    return response.json()


def get_cart_items(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get('https://api.moltin.com/v2/carts/:reference/items', headers=headers)
    response.raise_for_status()

    return response.json()


def get_inventory(token, prodict_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/inventories/{prodict_id}', headers=headers)
    response.raise_for_status()

    return response.json()


def get_product_image_url(token, product):

    pprint(product)

    image_id = product.get('data').get('relationships').get('main_image').get('data').get('id')

    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/files/{image_id}', headers=headers)
    response.raise_for_status()

    return response.json().get('data').get('link').get('href')


def get_product_unit(product):

    unit, = product.get('data').get('attributes').get('extensions').get('products(wegith)').keys()

    return unit


def get_product_price(product):

    return product.get('data').get("meta").get("display_price").get("with_tax").get("formatted")


def main():
    access_token = get_access_token(client_id)
    pprint(access_token)

    #products = get_all_products(access_token)
    #cart = get_cart(access_token)
    #pprint(products)

    #product = get_product(access_token, '07c9b380-a9bd-4faa-9cd6-3248f76f499f')

    #pprint(product)

    #inventory = get_inventory(access_token, '07c9b380-a9bd-4faa-9cd6-3248f76f499f')

    #pprint(inventory)

    #select_product = products[0]

    #added_product = {
    #    'data': {
    #        'id': select_product['id'],
    #        'type': 'cart_item',
    #        'quantity': 1
    #    }
    #}

    #pprint(added_product)

    #cart_after_add_product = add_product_to_cart(access_token, added_product)

    #new_cart = get_cart_items(access_token)
    #pprint(new_cart)
    product = get_product(access_token, '07c9b380-a9bd-4faa-9cd6-3248f76f499f')
    pprint(product)

    #product_url = get_product_image_url(access_token, product)
    #print(product_url)

    unit = get_product_unit(access_token, product)

    print(unit)


if __name__ == '__main__':
    main()

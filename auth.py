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

    access_token = response.json()['access_token']
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
        ':id': product_id
    }

    response = requests.get(f'https://api.moltin.com/v2/products/{product_id}', headers=headers)
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


def main():
    access_token = get_access_token(client_id)
    products = get_all_products(access_token)['data']
    #cart = get_cart(access_token)

    pprint(products[0])

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


if __name__ == '__main__':
    main()
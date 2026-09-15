"""Run with pytest. Uses isolated SQLite and makes no live service requests."""
import os

# Set before importing application models; never connect tests to a live database.
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['JWT_SECRET_KEY'] = 'guest-tests-only-a-long-signing-key-never-use-in-production'
os.environ['SUPABASE_URL'] = 'https://example.supabase.co'
os.environ['SUPABASE_SECRET_KEY'] = 'test-only-storage-key'

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.security import JWT_SECRET_KEY, create_access_token, create_refresh_token, decode_refresh_token, hash_password
from app.db.database import Base, get_db
from app.models.cart import CartItem
from app.models.favorite import Favorite
from app.models.order import Order, OrderStatus
from app.models.product import Product, ProductItem
from app.models.rating import Rating
from app.models.user import User


@pytest.fixture
def setup():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions() as db:
        product = Product(name='Example phone', description='Original description', price=100, category='Smartphones')
        db.add(product)
        db.flush()
        db.add(ProductItem(product_id=product.id, sku='PHONE-1', stock=20, reserved_stock=0, stock_limit=2))
        user = User(name='Customer', username='customer', email='customer@example.com', password_hash=hash_password('test-password'), role='customer', is_active=True, is_verified=True)
        db.add(user)
        db.commit()
        user_id = user.id
    def override_db():
        with sessions() as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        yield client, sessions, user_id
    app.dependency_overrides.clear()
    engine.dispose()


def headers(token):
    return {'Authorization': f'Bearer {token}'}


def guest(client):
    response = client.post('/api/v1/auth/guest')
    assert response.status_code == 200, response.text
    return response.json()


def test_guest_cart_survives_refresh_and_is_isolated(setup):
    client, sessions, _ = setup
    first, second = guest(client), guest(client)
    response = client.post('/api/v1/cart/', headers=headers(first['access_token']), json={'product_id': 1, 'quantity': 2})
    assert response.status_code == 200, response.text
    cart_id = response.json()['id']
    assert client.get('/api/v1/cart/', headers=headers(second['access_token'])).json() == []
    assert client.put(f'/api/v1/cart/{cart_id}/increment', headers=headers(second['access_token'])).status_code == 404
    refreshed = client.post('/api/v1/auth/refresh', json={'refresh_token': first['refresh_token']})
    assert refreshed.status_code == 200, refreshed.text
    token = refreshed.json()['access_token']
    restored = client.get('/api/v1/cart/', headers=headers(token)).json()
    assert restored[0]['quantity'] == 2
    me = client.get('/api/v1/auth/me', headers=headers(token))
    assert me.json()['role'] == 'guest'
    assert client.get('/api/v1/admin/dashboard', headers=headers(token)).status_code == 403
    with sessions() as db:
        assert db.get(ProductItem, 1).reserved_stock == 2


def test_guest_can_favorite_review_checkout_and_cancel(setup):
    client, sessions, _ = setup
    token = guest(client)['access_token']
    auth = headers(token)
    assert client.post('/api/v1/favorites/', headers=auth, json={'product_id': 1}).status_code == 200
    assert client.post('/api/v1/ratings/', headers=auth, json={'product_id': 1, 'rating': 5, 'comment': 'Nice'}).status_code == 200
    assert client.post('/api/v1/cart/', headers=auth, json={'product_id': 1, 'quantity': 1}).status_code == 200
    order = client.post('/api/v1/orders/', headers=auth, json={})
    assert order.status_code == 200, order.text
    order_id = order.json()['id']
    assert client.get('/api/v1/orders/', headers=auth).json()[0]['id'] == order_id
    outsider = headers(guest(client)['access_token'])
    assert client.get(f'/api/v1/orders/{order_id}', headers=outsider).status_code == 404
    assert client.patch(f'/api/v1/orders/{order_id}/status', headers=auth, json={'status': 'DONE'}).status_code == 403
    cancelled = client.patch(f'/api/v1/orders/{order_id}/cancel', headers=auth)
    assert cancelled.status_code == 200, cancelled.text
    with sessions() as db:
        assert db.get(ProductItem, 1).reserved_stock == 0


def test_signin_merge_preserves_quantities_stock_history_and_is_idempotent(setup):
    client, sessions, user_id = setup
    anonymous = guest(client)
    guest_id = int(decode_refresh_token(anonymous['refresh_token'])['sub'])
    account = headers(create_access_token(user_id))
    for auth, quantity in [(headers(anonymous['access_token']), 2), (account, 3)]:
        assert client.post('/api/v1/cart/', headers=auth, json={'product_id': 1, 'quantity': quantity}).status_code == 200
        assert client.post('/api/v1/favorites/', headers=auth, json={'product_id': 1}).status_code == 200
        assert client.post('/api/v1/ratings/', headers=auth, json={'product_id': 1, 'rating': 4}).status_code == 200
    with sessions() as db:
        db.add(Order(user_id=guest_id, status=OrderStatus.PENDING, total_amount=100))
        db.commit()
    for _ in range(2):
        response = client.post('/api/v1/auth/guest/merge', headers=account, json={'refresh_token': anonymous['refresh_token']})
        assert response.status_code == 200, response.text
    cart = client.get('/api/v1/cart/', headers=account).json()
    assert len(cart) == 1 and cart[0]['quantity'] == 5
    with sessions() as db:
        assert db.get(ProductItem, 1).reserved_stock == 5
        assert db.query(CartItem).filter_by(user_id=guest_id).count() == 0
        assert db.query(Favorite).filter_by(user_id=user_id).count() == 1
        assert db.query(Rating).filter_by(user_id=user_id).count() == 1
        assert db.query(Order).filter_by(user_id=user_id).count() == 1
        assert db.get(Product, 1).name == 'Example phone'
    assert client.get('/api/v1/cart/', headers=headers(anonymous['access_token'])).status_code == 403
    assert client.post('/api/v1/auth/refresh', json={'refresh_token': anonymous['refresh_token']}).status_code == 403


def test_guest_cannot_merge_an_account_or_gain_admin_after_role_change(setup):
    client, sessions, user_id = setup
    anonymous = guest(client)
    guest_id = int(decode_refresh_token(anonymous['refresh_token'])['sub'])
    assert client.post('/api/v1/auth/guest/merge', headers=headers(anonymous['access_token']), json={'refresh_token': create_refresh_token(user_id)}).status_code == 403
    assert client.post('/api/v1/auth/guest/merge', headers=headers(create_access_token(user_id)), json={'refresh_token': create_refresh_token(user_id)}).status_code == 401
    with sessions() as db:
        db.get(User, guest_id).role = 'admin'
        db.commit()
    assert client.get('/api/v1/admin/dashboard', headers=headers(anonymous['access_token'])).status_code == 401
    assert client.post('/api/v1/auth/refresh', json={'refresh_token': anonymous['refresh_token']}).status_code == 401


def test_expired_tampered_and_wrong_token_types_are_rejected(setup):
    client, _, user_id = setup
    expired = jwt.encode({'sub': str(user_id), 'type': 'guest_refresh', 'exp': 1}, JWT_SECRET_KEY, algorithm='HS256')
    for token in [expired, 'not-a-token', create_access_token(user_id)]:
        assert client.post('/api/v1/auth/refresh', json={'refresh_token': token}).status_code == 401
    invalid_sub = jwt.encode({'sub': 'invalid', 'type': 'access'}, JWT_SECRET_KEY, algorithm='HS256')
    assert client.get('/api/v1/auth/me', headers=headers(invalid_sub)).status_code == 401

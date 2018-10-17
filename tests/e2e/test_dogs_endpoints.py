"""Test for e2e Dogs model."""

import pytest

from app import db
from api import ALL_DOGS
from models import Dogs


@pytest.fixture
def dog_instance(client):
    dog = Dogs(name='tester')
    dog.save()
    return dog


@pytest.fixture
def mock_memcache_get(mocker):
    """Mock pymemcache to mimic memcache behaviour"""
    mocked = mocker.patch(
        'pymemcache.client.base.Client.get',
    )
    return mocked


@pytest.fixture
def mock_memcache_delete(mocker):
    """Mock pymemcache to mimic memcache behaviour"""
    mocked = mocker.patch(
        'pymemcache.client.base.Client.delete',
    )
    return mocked


@pytest.fixture
def mock_memcache_set(mocker):
    """Mock pymemcache to mimic memcache behaviour"""
    mocked = mocker.patch(
        'pymemcache.client.base.Client.set',
    )
    return mocked


@pytest.mark.parametrize('post_data', (
    # Cases where correct data is posted to '/dog/'-endpoint.
    {'name': 'name1', 'height': 1},
    {'name': 'name2', 'age': 1},
    {'name': 'name3', 'length': 1},
    {'name': 3, 'length': 1},
    {'name': 'name4', 'gender': 'male'},
    {'name': 'name5', 'gender': 'female'},
))
def test_return_201_status_with_correct_data_posted(
    post_data,
    client,
    mock_memcache_delete,
):
    """Should return 201 return status with correct data posted."""
    # when ... POST is made with correct data
    response = client.post('/dog/', data=post_data)

    # then
    # ... response is created and contains data posted,
    # ... and memcached modified correctly.
    assert response.status_code == 201
    assert mock_memcache_delete.called_once_with(ALL_DOGS)
    assert response.get_json()['name'] == str(post_data['name'])


@pytest.mark.parametrize('post_data', (
    # Cases where incorrect data is posted to '/dog/'-endpoint.
    {},
    {'name': 'name', 'height': -1},
    {'name': 'name', 'age': -1},
    {'name': 'name', 'length': -1},
    {'name': 'name', 'gender': 'whatever'},
))
def test_return_validation_errors_for_incorrect_data_post(post_data, client):
    """Should return validation errors for incorrect data posted."""

    # when ... POST request is made to '/dog/'-endpoint
    response = client.post(
        '/dog/',
        data=post_data,
    )

    # then
    # ... response contains error status from webargs
    assert response.status_code == 422


def test_returns_dogs_list_with_get_request(
    client,
    mock_memcache_set,
    dog_instance,
):
    """Should return list of all dogs in with a GET-LIST request."""
    # when ... GET request is made to 'dog'-endpoint
    response = client.get('/dog/')

    # then
    # ... response is success and one created record,
    # ... and memcache set correctly.
    assert response.status_code == 200
    assert mock_memcache_set.called_once_with(str(dog_instance.id))
    assert len(response.get_json()) == 1


def test_deletion_of_existing_dog_object(client, dog_instance):
    """Should delete existing row in Dogs model."""
    # given ... one dog instance in database.
    db.session.query(Dogs).count() == 1

    # when ... DELETE request is made to 'dog/<id>/'-endpoint
    response = client.delete(
        '/dog/{}/'.format(dog_instance.id),
    )

    # then
    # ... response contains success status
    # ... and no data in database.
    assert response.status_code == 200
    assert db.session.query(Dogs).count() == 0


def test_returns_target_dog_with_get_request(client, dog_instance):
    """Should return target dog in with a GET request."""
    # when ... GET request is made to 'dog'-endpoint
    response = client.get(
        '/dog/{}/'.format(dog_instance.id),
    )

    # then ... response is success and target record pulled.
    assert response.status_code == 200
    assert dog_instance.id == response.get_json().get('id')


@pytest.mark.parametrize('post_data', (
    # Cases where correct data is posted to '/dog_update/'-endpoint.
    # Other cases are already covered in above test.
    {'name': 'name1', 'height': 1},
    {'name': 'name2', 'age': 1},
    {'name': 'name3', 'length': 1},
    {'name': 'name4', 'gender': 'male'},
    {'name': 'name5', 'gender': 'female'},
))
def test_return_success_on_updating_dog_object_correctly(
    post_data,
    client,
    dog_instance,
    mock
):
    """Should return success on updating existing row in Dogs model."""
    # when ... PUT request is made to 'dog_update/'-endpoint
    post_data.update({'id': dog_instance.id})
    response = client.put(
        '/dog_update/',
        data=post_data,
    )

    # then
    # ... response contains success status
    # ... and data updated in database.
    dog = db.session.query(Dogs).filter_by(id=dog_instance.id).one()
    assert response.status_code == 200
    assert dog.name == post_data['name']


@pytest.mark.parametrize('update_data', (
    # Cases where incorrect data is posted to '/dog_update/'-endpoint.
    # Other cases are already covered in above test.
    {},
    {'name': 'name'},
    {'id': 1},
    {'id': 0, 'name': 'name'},
))
def test_return_validation_errors_for_incorrect_data_on_update(update_data, client):
    """Should return validation errors for incorrect data send on PUT."""

    # when ... PUT request is made to '/dog_update/'-endpoint
    response = client.put(
        '/dog_update/',
        data=update_data,
    )

    # then
    # ... response contains error status from webargs-library
    assert response.status_code == 422

"""Test for e2e Dogs model."""

import pytest

from app import db
from api import ALL_DOGS
from models import Dogs


memcache_response = b"{'name': 'tester', 'age': None, " \
                    b"'height': None, 'fur_color': '', " \
                    b"'gender': '', 'id': 1, " \
                    b"'updated_on': '2018-10-18T05:03:00', " \
                    b"'created_on': '2018-10-18T05:03:00', " \
                    b"'breed': 'Unknown', 'length': None}"


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
        return_value=memcache_response,
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
    dog_instance,
    mock_memcache_set,
    mock_memcache_get,
):
    """Should return list of all dogs in with a GET-LIST request."""
    # when ... GET request is made to 'dog'-endpoint
    mock_memcache_get.return_value = None
    response = client.get('/dog/')

    # then
    # ... response is success and one created record,
    # ... and memcache set and get correctly.
    assert response.status_code == 200
    assert mock_memcache_set.called_once_with(str(dog_instance.id))
    assert mock_memcache_get.called_once_with(str(dog_instance.id))
    assert len(response.get_json()) == 1


def test_returns_dogs_list_with_get_request_from_memcache(
    client,
    dog_instance,
    mock_memcache_get,
):
    """Should return list of all dogs in with a GET-LIST request from memcache."""
    # when ... GET request is made to 'dog'-endpoint
    mock_memcache_get.return_value = b"[" + mock_memcache_get.return_value + b"]"
    response = client.get('/dog/')

    # then
    # ... response is success and one created record,
    # ... and memcache get correctly.
    assert response.status_code == 200
    assert mock_memcache_get.call_count == 2
    assert len(response.get_json()) == 1


def test_deletion_of_existing_dog_object(
    client,
    dog_instance,
    mock_memcache_delete,
):
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
    # ... and two keys deleted from memcache.
    assert response.status_code == 200
    assert mock_memcache_delete.call_count == 2
    assert db.session.query(Dogs).count() == 0


def test_returns_target_dog_with_get_request(
    client,
    dog_instance,
    mock_memcache_set,
    mock_memcache_get,
):
    """Should return target dog in with a GET request."""
    # when ... GET request is made to 'dog'-endpoint
    response = client.get(
        '/dog/{}/'.format(dog_instance.id),
    )

    # then
    # ... response is success and target record pulled.
    # ... memcache called on set and get.
    assert response.status_code == 200
    assert mock_memcache_set.called_once(str(dog_instance.id))
    assert mock_memcache_get.call_count == 2
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
    mock_memcache_delete,
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
    assert mock_memcache_delete.called_once_with(str(dog_instance.id))
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


@pytest.mark.parametrize('http_method,endpoint', (
    # Cases where requesting for non existing resources.
    ('put', '/dog_update/',),
    ('get', '/dog/5/',),
    ('delete', '/dog/1/',),
))
def test_return_404_error_for_not_finding_resource_for_endpoints(
    http_method,
    endpoint,
    client,
):
    """Should return 404 error for not finding resource for endpoints."""

    # when ... a request is made to '/dog_update/'-endpoint
    endpoint = endpoint.format()
    response = getattr(client, http_method)(
        endpoint,
        data={'id': 1, 'name': 'name'},
    )

    # then
    # ... response contains error status not found
    assert response.status_code == 404

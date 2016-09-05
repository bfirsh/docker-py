import unittest

import docker


class ImageTest(unittest.TestCase):

    def test_build(self):
        pass

    def test_list(self):
        client = docker.from_env()
        image = client.images.pull('alpine:latest')
        assert image.id in get_ids(client.images.list())

    def test_list_with_repository(self):
        client = docker.from_env()
        image = client.images.pull('alpine:latest')
        assert image.id in get_ids(client.images.list('alpine'))
        assert image.id in get_ids(client.images.list('alpine:latest'))

    def test_pull(self):
        client = docker.from_env()
        image = client.images.pull('alpine:latest')
        assert 'alpine:latest' in image.attrs['RepoTags']

    def test_tag_and_remove(self):
        repo = 'dockersdk.tests.images.test_tag'
        tag = 'some-tag'
        identifier = '{}:{}'.format(repo, tag)

        client = docker.from_env()
        image = client.images.pull('alpine:latest')

        image.tag(repo, tag)
        assert image.id in get_ids(client.images.list(repo))
        assert image.id in get_ids(client.images.list(identifier))

        client.images.remove(identifier)
        assert image.id not in get_ids(client.images.list(repo))
        assert image.id not in get_ids(client.images.list(identifier))

        assert image.id in get_ids(client.images.list('alpine:latest'))


def get_ids(images):
    return [i.id for i in images]

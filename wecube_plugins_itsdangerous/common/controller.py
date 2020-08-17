# coding=utf-8

from __future__ import absolute_import

import falcon
from talos.common.controller import CollectionController
from talos.common.controller import ItemController
from talos.core import exceptions


class Collection(CollectionController):
    def on_get(self, req, resp, **kwargs):
        self._validate_method(req)
        refs = []
        count = 0
        criteria = self._build_criteria(req)
        if criteria:
            refs = self.list(req, criteria, **kwargs)
            count = self.count(req, criteria, results=refs, **kwargs)
        resp.json = {'code': 200, 'status': 'OK', 'data': {'count': count, 'data': refs}, 'message': 'success'}

    def on_post(self, req, resp, **kwargs):
        self._validate_method(req)
        self._validate_data(req)
        resp.json = {'code': 200, 'status': 'OK', 'data': self.create(req, req.json, **kwargs), 'message': 'success'}
        resp.status = falcon.HTTP_201


class Item(ItemController):
    def on_get(self, req, resp, **kwargs):
        self._validate_method(req)
        ref = self.get(req, **kwargs)
        if ref is not None:
            resp.json = {'code': 200, 'status': 'OK', 'data': ref, 'message': 'success'}
        else:
            raise exceptions.NotFoundError(resource=self.resource.__name__)

    def on_patch(self, req, resp, **kwargs):
        self._validate_method(req)
        self._validate_data(req)
        ref_before, ref_after = self.update(req, req.json, **kwargs)
        if ref_after is not None:
            resp.json = {'code': 200, 'status': 'OK', 'data': ref_after, 'message': 'success'}
        else:
            raise exceptions.NotFoundError(resource=self.resource.__name__)

    def on_delete(self, req, resp, **kwargs):
        self._validate_method(req)
        ref, details = self.delete(req, **kwargs)
        if ref:
            resp.json = {'code': 200, 'status': 'OK', 'data': {'count': ref, 'data': details}, 'message': 'success'}
        else:
            raise exceptions.NotFoundError(resource=self.resource.__name__)

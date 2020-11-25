import { req as request, baseURL } from './base'
import { pluginErrorMessage } from './base-plugin'
let req = request
if (window.request) {
  req = {
    post: (url, ...params) => pluginErrorMessage(window.request.post(baseURL + url, ...params)),
    get: (url, ...params) => pluginErrorMessage(window.request.get(baseURL + url, ...params)),
    delete: (url, ...params) => pluginErrorMessage(window.request.delete(baseURL + url, ...params)),
    put: (url, ...params) => pluginErrorMessage(window.request.put(baseURL + url, ...params)),
    patch: (url, ...params) => pluginErrorMessage(window.request.patch(baseURL + url, ...params))
  }
}

export const getTableData = url => req.get(url)
export const addTableRow = (url, data) => req.post(`${url}`, data)
export const editTableRow = (url, id, data) => req.patch(`/${url}/${id}`, data)
export const deleteTableRow = (url, id) => req.delete(`/${url}/${id}`)

export const boxDetect = (id, data) => req.post(`boxes/${id}/run`, data)

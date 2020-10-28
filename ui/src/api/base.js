import { setCookie, getCookie } from '../pages/util/cookie.js'
import Vue from 'vue'
import axios from 'axios'
export const baseURL = '/itsdangerous/ui/v1'
export const req = axios.create({
  withCredentials: true,
  baseURL,
  timeout: 50000
})

const throwError = res => new Error(res.message || 'error')
req.interceptors.response.use(
  res => {
    if (res.data.code === 200) {
      if (res.data.status.startsWith('ERR')) {
        const errorMes = Array.isArray(res.data.data)
          ? res.data.data.map(_ => _.errorMessage).join('<br/>')
          : res.data.statusMessage
        Vue.prototype.$Notice.error({
          title: 'Error',
          desc: errorMes,
          duration: 0
        })
      }
      return {
        ...res.data,
        user: res.headers['username'] || ' - '
      }
    } else {
      return {
        data: throwError(res)
      }
    }
  },
  error => {
    const { response } = error
    Vue.prototype.$Notice.error({
      title: 'error',
      desc:
        (response.data &&
          'status:' +
            response.data.status +
            '<br/> error:' +
            response.data.error +
            '<br/> message:' +
            response.data.message) ||
        'error'
    })
    return new Promise((resolve, reject) => {
      resolve({
        data: throwError(error)
      })
    })
  }
)

let refreshRequest = null
req.interceptors.request.use(
  config => {
    return new Promise((resolve, reject) => {
      const currentTime = new Date().getTime()
      const accessToken = getCookie('accessToken')
      if (accessToken && config.url !== '/auth/v1/api/login') {
        const expiration = getCookie('accessTokenExpirationTime') * 1 - currentTime
        if (expiration < 1 * 60 * 1000 && !refreshRequest) {
          refreshRequest = axios.get('/auth/v1/api/token', {
            headers: {
              Authorization: 'Bearer ' + getCookie('refreshToken')
            }
          })
          refreshRequest.then(
            res => {
              setCookie(res.data.data)
              config.headers.Authorization = 'Bearer ' + res.data.data.find(t => t.tokenType === 'accessToken').token
              refreshRequest = null
              resolve(config)
            },
            // eslint-disable-next-line handle-callback-err
            err => {
              refreshRequest = null
              window.location.href = window.location.origin + window.location.pathname + '#/login'
            }
          )
        }
        if (expiration < 1 * 60 * 1000 && refreshRequest) {
          refreshRequest.then(
            res => {
              setCookie(res.data.data)
              config.headers.Authorization = 'Bearer ' + res.data.data.find(t => t.tokenType === 'accessToken').token
              refreshRequest = null
              resolve(config)
            },
            // eslint-disable-next-line handle-callback-err
            err => {
              refreshRequest = null
              window.location.href = window.location.origin + window.location.pathname + '#/login'
            }
          )
        }
        if (expiration > 1 * 60 * 1000) {
          config.headers.Authorization = 'Bearer ' + accessToken
          resolve(config)
        }
      } else {
        resolve(config)
      }
    })
  },
  error => {
    return Promise.reject(error)
  }
)

function setHeaders (obj) {
  Object.keys(obj).forEach(key => {
    req.defaults.headers.common[key] = obj[key]
  })
}

export { setHeaders }

import 'regenerator-runtime/runtime'
import router from './router-plugin'
import zhCN from './locale/i18n/zh-CN.json'
import enUS from './locale/i18n/en-US.json'

window.locale('zh-CN', zhCN)
window.locale('en-US', enUS)

window.addRoutes && window.addRoutes(router, 'cmdb')

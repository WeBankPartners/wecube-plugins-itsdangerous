import 'regenerator-runtime/runtime'
import router from './router-plugin'
import 'view-design/dist/styles/iview.css'
import './locale/i18n'
import { validate } from '@/assets/js/validate.js'
import { commonUtil } from '@/pages/util/common-util.js'
import '@/assets/css/local.bootstrap.css'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import VeeValidate from '@/assets/veeValidate/VeeValidate'
import jquery from 'jquery'
import zhCN from '@/locale/i18n/zh-CN.json'
import enUS from '@/locale/i18n/en-US.json'

import PageTable from '@/pages/components/table-page/page'
import ModalComponent from '@/pages/components/modal'

window.addOptions({
  JQ: jquery,
  $commonUtil: commonUtil,
  $validate: validate
})

window.component('PageTable', PageTable)
window.component('ModalComponent', ModalComponent)
window.use(VeeValidate)

window.locale('zh-CN', zhCN)
window.locale('en-US', enUS)
const implicitRoute = {
  'dangerousIndex/boxes': { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
  'dangerousIndex/policy': { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
  'dangerousIndex/rule': { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
  'dangerousIndex/subjects': { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
  'dangerousIndex/targets': { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
  'dangerousIndex/match-params': { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' },
  'dangerousIndex/plugin-params': { 'zh-CN': '高危规则配置', 'en-US': 'Dangerous Config' }
}
window.addImplicitRoute(implicitRoute)
window.addRoutes && window.addRoutes(router, 'dangerous')

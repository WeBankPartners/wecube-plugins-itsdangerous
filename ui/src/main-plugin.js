import 'regenerator-runtime/runtime'
import router from './router'
import 'view-design/dist/styles/iview.css'
import './locale/i18n'
import { validate } from '@/assets/js/validate.js'
import { commonUtil } from '@/pages/util/common-util.js'
import '@/assets/css/local.bootstrap.css'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import VeeValidate from '@/assets/veeValidate/VeeValidate'
import jquery from 'jquery'
import zhCN from '@/assets/locale/i18n/zh-CN.json'
import enUS from '@/assets/locale/i18n/en-US.json'

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

window.addRoutes && window.addRoutes(router, 'dangerous')

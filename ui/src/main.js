import '@/assets/css/local.bootstrap.css'
import { validate } from '@/assets/js/validate.js'
import { commonUtil } from '@/pages/util/common-util.js'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import jquery from 'jquery'
import 'regenerator-runtime/runtime'
import ViewUI from 'view-design'
import locale from 'view-design/dist/locale/en-US'
// import 'view-design/dist/styles/iview.css'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import App from './App.vue'
import './locale/i18n'
import router from './router'
import './styles/index.less'

import ModalComponent from '@/pages/components/modal'
import DangerousPageTable from '@/pages/components/table-page/page'

Vue.prototype.$validate = validate
Vue.prototype.$itsCommonUtil = commonUtil
Vue.prototype.JQ = jquery
Vue.component('DangerousPageTable', DangerousPageTable)
Vue.component('ModalComponent', ModalComponent)

Vue.config.productionTip = false

Vue.use(ViewUI, {
  transfer: true,
  size: 'default',
  VueI18n,
  locale
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

import 'core-js/stable'
import 'regenerator-runtime/runtime'
import Vue from 'vue'
import VueHighlightJS from 'vue-highlight.js'
import 'vue-highlight.js/lib/allLanguages'
import 'highlight.js/styles/default.css'
import App from './App.vue'
import router from './router'
import ViewUI from 'view-design'
import 'view-design/dist/styles/iview.css'
import VueI18n from 'vue-i18n'
import locale from 'view-design/dist/locale/en-US'
import './locale/i18n'
import { validate } from '@/assets/js/validate.js'
import '@/assets/css/local.bootstrap.css'
import 'bootstrap/dist/js/bootstrap.min.js'
import 'font-awesome/css/font-awesome.css'
import VeeValidate from '@/assets/veeValidate/VeeValidate'
import jquery from 'jquery'

import PageTable from '@/pages/components/table-page/page'
import ModalComponent from '@/pages/components/modal'

Vue.prototype.$validate = validate
Vue.prototype.JQ = jquery
Vue.component('PageTable', PageTable)
Vue.component('ModalComponent', ModalComponent)
Vue.use(VeeValidate)

Vue.config.productionTip = false

Vue.use(ViewUI, {
  transfer: true,
  size: 'default',
  VueI18n,
  locale
})

Vue.use(VueHighlightJS)

router.beforeEach((to, from, next) => {
  if (window.myMenus) {
    let hasPermission = [].concat(...window.myMenus.map(_ => _.submenus)).find(_ => _.link === to.path)
    if (hasPermission || to.path === '/homepage' || to.path.startsWith('/setting') || to.path === '/404') {
      /* has permission */
      next()
    } else {
      /* has no permission */
      next('/404')
    }
  } else {
    next()
  }
})
new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

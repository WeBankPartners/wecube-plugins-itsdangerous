import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: 'IndexPage',
      redirect: '/homepage/policy',
      component: () => import('@/pages/index'),
      children: [
        {
          path: '/homepage',
          name: 'homepage',
          component: () => import('@/pages/home-page'),
          params: {},
          props: true,
          children: [
            {
              path: 'policy',
              name: 'policy',
              title: '对象管理',
              meta: {},
              component: () => import('@/pages/policy')
            },
            {
              path: 'rule',
              name: 'rule',
              title: '组管理',
              meta: {},
              component: () => import('@/pages/rule')
            },
            {
              path: 'test3',
              name: 'test3',
              title: '阈值配置',
              meta: {},
              component: () => import('@/pages/test3')
            },
            {
              path: 'test4',
              name: 'test4',
              title: '关键字配置',
              meta: {},
              component: () => import('@/pages/test4')
            },
            {
              path: 'test5',
              name: 'test5',
              title: '资源层级',
              meta: {},
              component: () => import('@/pages/test5')
            },
            {
              path: 'test6',
              name: 'test6',
              title: '资源层级',
              meta: {},
              component: () => import('@/pages/test6')
            }
          ]
        }
      ]
    }
  ]
})
